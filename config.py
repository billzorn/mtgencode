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
reserved_marker = '\r'
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
