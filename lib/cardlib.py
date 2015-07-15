# card representation
import re

import utils
import transforms
from manalib import Manacost, Manatext

# These are used later to determine what the fields of the Card object are called.
# Define them here because they have nothing to do with the actual format.
field_name = 'name'
field_rarity = 'rarity'
field_cost = 'cost'
field_supertypes = 'supertypes'
field_types = 'types'
field_subtypes = 'subtypes'
field_loyalty = 'loyalty'
field_pt = 'pt'
field_text = 'text'
field_other = 'other' # it's kind of a pseudo-field

# Import the labels, because these do appear in the encoded text.
field_label_name = utils.field_label_name
field_label_rarity = utils.field_label_rarity
field_label_cost = utils.field_label_cost
field_label_supertypes = utils.field_label_supertypes
field_label_types = utils.field_label_types
field_label_subtypes = utils.field_label_subtypes
field_label_loyalty = utils.field_label_loyalty
field_label_pt = utils.field_label_pt
field_label_text = utils.field_label_text

fieldnames = [
    field_name,
    field_rarity,
    field_cost,
    field_supertypes,
    field_types,
    field_subtypes,
    field_loyalty,
    field_pt,
    field_text,
]

fmt_ordered_default = [
    field_name,
    field_supertypes,
    field_types,
    field_loyalty,
    field_subtypes,
    field_pt,
    field_cost,
    field_text,
]

fmt_labeled_default = {
    field_name : field_label_name,
    field_rarity : field_label_rarity,
    field_cost : field_label_cost,
    field_supertypes : field_label_supertypes,
    field_types : field_label_types,
    field_loyalty : field_label_loyalty,
    field_pt : field_label_pt,
    field_text : field_label_text,
}

# sanity test if a card's fields look plausible
def fields_check_valid(fields):
    # all cards must have a name and a type
    if not field_name in fields:
        return False
    if not field_types in fields:
        return False
    # creatures have p/t, other things don't
    iscreature = False
    for idx, value in fields[field_types]:
        if 'creature' in value:
            iscreature = True
    if iscreature:
        return field_pt in fields
    else:
        return not field_pt in fields

# These functions take a bunch of source data in some format and turn
# it into nicely labeled fields that we know how to initialize a card from.
# Both return a dict that maps field names to lists of possible values,
# paired with the index that we read that particular field value from.
# So, {fieldname : [(idx, value), (idx, value)...].
# Usually we want these lists to be length 1, but you never know.

# Of course to make things nice and simple, that dict is the third element
# of a triple that reports parsing success and valid success as its 
# first two elements.

# This whole things assumes the json format of mtgjson.com.

# Here's a brief list of relevant fields:
# name - string
# names - list (used for split, flip, and double-faced)
# manaCost - string
# cmc - number
# colors - list
# type - string (the whole big long damn thing)
# supertypes - list
# types - list
# subtypes - list
# text - string
# power - string
# toughness - string
# loyalty - number

# And some less useful ones, in case they're wanted for something:
# layout - string
# rarity - string
# flavor - string
# artis - string
# number - string
# multiverseid - number
# variations - list
# imageName - string
# watermark - string
# border - string
# timeshifted - boolean
# hand - number
# life - number
# reserved - boolean
# releaseDate - string
# starter - boolean

def fields_from_json(src_json):
    parsed = True
    valid = True
    fields = {}

    # we hardcode in what the things are called in the mtgjson format
    if 'name' in src_json:
        name_val = src_json['name'].lower()
        name_orig = name_val
        name_val = transforms.name_pass_1_sanitize(name_val)
        name_val = utils.to_ascii(name_val)
        fields[field_name] = [(-1, name_val)]
    else:
        name_orig = ''
        parsed = False

    # return the actual Manacost object
    if 'manaCost' in src_json:
        cost =  Manacost(src_json['manaCost'], fmt = 'json')
        valid = valid and cost.valid
        parsed = parsed and cost.parsed
        fields[field_cost] = [(-1, cost)]

    if 'supertypes' in src_json:
        fields[field_supertypes] = [(-1, map(lambda s: utils.to_ascii(s.lower()), 
                                             src_json['supertypes']))]

    if 'types' in src_json:
        fields[field_types] = [(-1, map(lambda s: utils.to_ascii(s.lower()), 
                                        src_json['types']))]
    else:
        parsed = False

    if 'subtypes' in src_json:
        fields[field_subtypes] = [(-1, map(lambda s: utils.to_ascii(s.lower()), 
                                           src_json['subtypes']))]

    if 'loyalty' in src_json:
        fields[field_loyalty] = [(-1, utils.to_unary(str(src_json['loyalty'])))]

    p_t = ''
    if 'power' in src_json:
        p_t = utils.to_ascii(utils.to_unary(src_json['power'])) + '/' # hardcoded
        valid = False
        if 'toughness' in src_json:
            p_t = p_t + utils.to_ascii(utils.to_unary(src_json['toughness']))
            valid = True
    elif 'toughness' in src_json:
        p_t = '/' + utils.to_ascii(utils.to_unary(src_json['toughness'])) # hardcoded
        valid = False
    if p_t:
        fields[field_pt] = [(-1, p_t)]
        
    # similarly, return the actual Manatext object
    if 'text' in src_json:
        text_val = src_json['text'].lower()
        text_val = transforms.text_pass_1_strip_rt(text_val)
        text_val = transforms.text_pass_2_cardname(text_val, name_orig)
        text_val = transforms.text_pass_3_unary(text_val)
        text_val = transforms.text_pass_4a_dashes(text_val)
        text_val = transforms.text_pass_4b_x(text_val)
        text_val = transforms.text_pass_5_counters(text_val)
        text_val = transforms.text_pass_6_uncast(text_val)
        text_val = transforms.text_pass_7_choice(text_val)
        text_val = transforms.text_pass_8_equip(text_val)
        text_val = transforms.text_pass_9_newlines(text_val)
        text_val = transforms.text_pass_10_symbols(text_val)
        text_val = utils.to_ascii(text_val)
        text_val = text_val.strip()
        mtext = Manatext(text_val, fmt = 'json')
        valid = valid and mtext.valid
        fields[field_text] = [(-1, mtext)]
    
    # we don't need to worry about bsides because we handle that in the constructor
    return parsed, valid and fields_check_valid(fields), fields


def fields_from_format(src_text, fmt_ordered, fmt_labeled, fieldsep):
    parsed = True
    valid = True
    fields = {}

    if fmt_labeled:
        labels = {fmt_labeled[k] : k for k in fmt_labeled}
        field_label_regex = '[' + ''.join(labels.keys()) + ']'
    def addf(fields, fkey, fval):
        if fkey in fields:
            fields[fkey] += [fval]
        else:
            fields[fkey] = [fval]

    textfields = src_text.split(fieldsep)
    idx = 0
    true_idx = 0
    for textfield in textfields:
        # ignore leading or trailing empty fields due to seps
        if textfield == '':
            if true_idx == 0 or true_idx == len(textfields) - 1:
                true_idx += 1
                continue
            # count the field index for other empty fields but don't add them
            else:
                idx += 1
                true_idx += 1
                continue

        lab = None
        if fmt_labeled:
            labs = re.findall(field_label_regex, textfield)
            # use the first label if we saw any at all
            if len(labs) > 0:
                lab = labs[0]
        # try to use the field label if we got one
        if lab and lab in labels:
            fname = labels[lab]
        # fall back to the field order specified
        elif idx < len(fmt_ordered):
            fname = fmt_ordered[idx]
        # we don't know what to do with this field: call it other
        else:
            fname = field_other
            parsed = False
            valid = False
        
        # specialized handling
        if fname in [field_cost]:
            fval = Manacost(textfield)
            parsed = parsed and fval.parsed
            valid = valid and fval.valid
            addf(fields, fname, (idx, fval))
        elif fname in [field_text]:
            fval = Manatext(textfield)
            valid = valid and fval.valid
            addf(fields, fname, (idx, fval))
        elif fname in [field_supertypes, field_types, field_subtypes]:
            addf(fields, fname, (idx, textfield.split()))
        else:
            addf(fields, fname, (idx, textfield))

        idx += 1
        true_idx += 1
        
    # again, bsides are handled by the constructor
    return parsed, valid and fields_check_valid(fields), fields

# Here's the actual Card class that other files should use.

class Card:
    '''card representation with data'''

    def __init__(self, src, fmt_ordered = fmt_ordered_default, 
                            fmt_labeled = None, 
                            fieldsep = utils.fieldsep):
        # source fields, exactly one will be set
        self.json = None
        self.raw = None
        # flags
        self.parsed = True
        self.valid = True # only records broken pt right now (broken as in, no /)
        # default values for all fields
        self.__dict__[field_name] = ''
        self.__dict__[field_rarity] = ''
        self.__dict__[field_cost] = Manacost('')
        self.__dict__[field_supertypes] = []
        self.__dict__[field_types] = []
        self.__dict__[field_subtypes] = []
        self.__dict__[field_loyalty] = ''
        self.__dict__[field_loyalty + '_value'] = None
        self.__dict__[field_pt] = ''
        self.__dict__[field_pt + '_p'] = None
        self.__dict__[field_pt + '_p_value'] = None
        self.__dict__[field_pt + '_t'] = None
        self.__dict__[field_pt + '_t_value'] = None
        self.__dict__[field_text] = Manatext('')
        self.__dict__[field_text + '_lines'] = []
        self.__dict__[field_text + '_words'] = []
        self.__dict__[field_other] = []
        self.bside = None
        # format-independent view of processed input
        self.fields = None # will be reset later

        # looks like a json object
        if isinstance(src, dict):
            if utils.json_field_bside in src:
                self.bside = Card(src[utils.json_field_bside],
                                  fmt_ordered = fmt_ordered,
                                  fmt_labeled = fmt_labeled,
                                  fieldsep = fieldsep)
            p_success, v_success, parsed_fields = fields_from_json(src)
            self.parsed = p_success
            self.valid = v_success
            self.fields = parsed_fields
        # otherwise assume text encoding
        else:
            sides = src.split(utils.bsidesep)
            if len(sides) > 1:
                self.bside = Card(utils.bsidesep.join(sides[1:]), 
                                  fmt_ordered = fmt_ordered,
                                  fmt_labeled = fmt_labeled,
                                  fieldsep = fieldsep)
            p_success, v_success, parsed_fields = fields_from_format(sides[0], fmt_ordered, 
                                                                     fmt_labeled,  fieldsep)
            self.parsed = p_success
            self.valid = v_success
            self.fields = parsed_fields
        # amusingly enough, both encodings allow infinitely deep nesting of bsides...

        # python name hackery
        if self.fields:
            for field in self.fields:
                # look for a specialized set function
                if hasattr(self, '_set_' + field):
                    getattr(self, '_set_' + field)(self.fields[field])
                # otherwise use the default one
                elif field in self.__dict__:
                    self.set_field_default(field, self.fields[field])
                # If we don't recognize the field, fail. This is a totally artificial
                # limitation; if we just used the default handler for the else case,
                # we could set arbitrarily named fields.
                else:
                    raise ValueError('python name mangling failure: unknown field for Card(): ' 
                                     + field)
        else:
            # valid but not parsed indicates that the card was apparently empty
            self.parsed = False

    # These setters are invoked via name mangling, so they have to match 
    # the field names specified above to be used. Otherwise we just
    # always fall back to the (uninteresting) default handler.

    # Also note that all fields come wrapped in pairs, with the first member
    # specifying the index the field was found at when parsing the card. These will
    # all be -1 if the card was parsed from (unordered) json.

    def set_field_default(self, field, values):
        for idx, value in values:
            self.__dict__[field] = value
            break # only use the first one...

    def _set_loyalty(self, values):
        for idx, value in values:
            self.__dict__[field_loyalty] = value
            try:
                self.__dict__[field_loyalty + '_value'] = int(value)
            except ValueError:
                self.__dict__[field_loyalty + '_value'] = None
                # Technically '*' could still be valid, but it's unlikely...
            break # only use the first one...

    def _set_pt(self, values):
        for idx, value in values:
            self.__dict__[field_pt] = value
            p_t = value.split('/') # hardcoded
            if len(p_t) == 2:
                self.__dict__[field_pt + '_p'] = p_t[0]
                try:
                    self.__dict__[field_pt + '_p_value'] = int(p_t[0])
                except ValueError:
                    self.__dict__[field_pt + '_p_value'] = None
                self.__dict__[field_pt + '_t'] = p_t[1]
                try:
                    self.__dict__[field_pt + '_t_value'] = int(p_t[1])
                except ValueError:
                    self.__dict__[field_pt + '_t_value'] = None
            else:
                self.valid = False
            break # only use the first one...
    
    def _set_text(self, values):
        for idx, value in values:
            mtext = value
            self.__dict__[field_text] = mtext
            fulltext = mtext.encode()
            if fulltext:
                self.__dict__[field_text + '_lines'] = map(Manatext, fulltext.split(utils.newline))
                self.__dict__[field_text + '_words'] = re.sub(utils.unletters_regex, 
                                                              ' ', 
                                                              fulltext).split()
            break # only use the first one...
        
    def _set_other(self, values):
        # just record these, we could do somthing unset valid if we really wanted
        for idx, value in values:
            self.__dict__[field_other] += [(idx, value)]

    # Output functions that produce various formats. encode() is specific to
    # the NN representation, use str() or format() for output intended for human
    # readers.

    def encode(self, fmt_ordered = fmt_ordered_default,
               fmt_labeled = None, fieldsep = utils.fieldsep,
               randomize_fields = False, randomize_mana = False,
               initial_sep = True, final_sep = True):
        outfields = []

        for field in fmt_ordered:
            if field in self.__dict__:
                outfield = self.__dict__[field]
                if outfield:
                    # specialized field handling for the ones that aren't strings (sigh)
                    if isinstance(outfield, list):
                        outfield_str = ' '.join(outfield)
                    elif isinstance(outfield, Manacost):
                        outfield_str = outfield.encode(randomize = randomize_mana)
                    elif isinstance(outfield, Manatext):
                        outfield_str = outfield.encode(randomize = randomize_mana)
                    else:
                        outfield_str = outfield

                    if fmt_labeled and field in fmt_labeled:
                        outfield_str = fmt_labeled[field] + outfield_str

                else:
                    outfield_str = ''

                outfields += [outfield_str]

            else:
                raise ValueError('unknown field for Card.encode(): ' + str(field))

        if randomize_fields:
            random.shuffle(outfields)
        if initial_sep:
            outfields = [''] + outfields
        if final_sep:
            outfields = outfields + ['']
        
        outstr = fieldsep.join(outfields)

        if self.bside:
            outstr = (outstr + utils.bsidesep 
                      + self.bside.encode(fmt_ordered = fmt_ordered,
                                          fmt_labeled = fmt_labeled,
                                          fieldsep = fieldsep,
                                          randomize_fields = randomize_fields, 
                                          randomize_mana = randomize_mana,
                                          initial_sep = initial_sep, final_sep = final_sep))

        return outstr
