import re

# Utilities for handling unicode, unary numbers, mana costs, and special symbols.
# For convenience we redefine everything from utils so that it can all be accessed
# from the utils module.

# separators
cardsep = '\n\n'
fieldsep = '|'
bsidesep = '\n'
newline = '\\'

# special indicators
dash_marker = '~'
bullet_marker = '='
this_marker = '@'
counter_marker = '%'
reserved_marker = '\v'
reserved_mana_marker = '$'
x_marker = 'X'
tap_marker = 'T'
untap_marker = 'Q'

# unambiguous synonyms
counter_rename = 'uncast'

# unary numbers
unary_marker = '&'
unary_counter = '^'
unary_max = 20
unary_exceptions = {
    25 : 'twenty' + dash_marker + 'five',
    30 : 'thirty',
    40 : 'forty',
    50 : 'fifly',
    100: 'one hundred',
    200: 'two hundred',
}

# field labels, to allow potential reordering of card format
field_label_name = '1'
field_label_rarity = '2'
field_label_cost = '3'
field_label_supertypes = '4'
field_label_types = '5'
field_label_subtypes = '6'
field_label_loyalty = '7'
field_label_pt = '8'
field_label_text = '9'
# one left, could use for managing bsides

# additional fields we add to the json cards
json_field_bside = 'bside'
json_field_set_name = 'setName'
