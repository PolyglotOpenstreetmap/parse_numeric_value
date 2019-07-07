# coding: utf8
from __future__ import unicode_literals

import re
from pprint import pprint

hundreds_tens_units_re = re.compile(r"""(?x)
      (
        (?P<hundreds>deux|trois|quatre|cinq|six|sept|huit|neuf)?
        (?P<hyphen_hundreds>[\s-])?
        (?P<hundred>cents?)
      (?P<hyphen_hundred>[\s-])?
      )?
      (
        (?P<from_11_to_16>onze|douze|treize|quatorze|quinze|seize)?
        (?P<ordinal_1>(premier|première)s?)?
        (?P<tens>dix|vingt|trente|quarante|cinquante|soixante|soixante-dix|septante|quatre-vingt|quatre-vingt-dix|nonante)?
        (?P<ordinal_30>trent)?
        (?P<hyphen_tens>-)?
      )?
      (
        (?P<units_ordinal_5>cinqu)?
        (?P<units>zéro|(et-| et )une?|deux|trois|quatre|cinq|six|sept|huit|neuf)?
        (?P<units_ordinal>quatr|neuv)?
        (?P<from_11_to_16_ordinal>onz|douz|treiz|quatorz|quinz|seiz)?
      )?
      (?P<ordinal>ième)?
      (?P<rest>.*)""")

numeric_lookup = {
    0: 'zéro', 1: ['un', 'une'], 2: 'deux', 3: 'trois', 4: 'quatre', 5: 'cinq',
    6: 'six', 7: 'sept', 8: 'huit', 9: 'neuf', 10: 'dix', 11: 'onze', 12: 'douze',
    13: 'treize', 14: 'quatorze', 15: 'quinze', 16: 'seize',
    17: 'dix-sept', 18: 'dix-huit', 19: 'dix-neuf',
    20: 'vingt', 30: 'trente', 40: 'quarante', 50: 'cinquante', 60: 'soixante',
    70: ['soixante-dix', 'septante'], 71: ['soixante-onze', 'septante-et-un'],
    72: ['soixante-douze', 'septante-deux'], 73: ['soixante-treize', 'septante-trois'],
    74: ['soixante-quatorze', 'septante-quatre'], 75: ['soixante-quinze', 'septante-cinq'],
    76: ['soixante-seize', 'septante-six'], 77: ['soixante-dix-sept', 'septante-sept'],
    78: ['soixante-dix-huit', 'septante-huit'], 79: ['soixante-dix-neuf', 'septante-neuf'],
    80: ['quatre-vingts', 'huitante', 'octante'],
    81: ['quatre-vingt-un', 'huitante-et-un', 'octante-et-un'],
    82: ['quatre-vingt-deux', 'huitante-deux', 'octante-deux'],
    83: ['quatre-vingt-trois', 'huitante-trois', 'octante-trois'],
    84: ['quatre-vingt-quatre', 'huitante-quatre', 'octante-quatre'],
    85: ['quatre-vingt-cinq', 'huitante-cinq', 'octante-cinq'],
    86: ['quatre-vingt-six', 'huitante-six', 'octante-six'],
    87: ['quatre-vingt-sept', 'huitante-sept', 'octante-sept'],
    88: ['quatre-vingt-huit', 'huitante-huit', 'octante-huit'],
    89: ['quatre-vingt-neuf', 'huitante-neuf', 'octante-neuf'],
    90: ['quatre-vingt-dix', 'nonante'], 91: ['quatre-vingt-onze', 'nonante-et-un'],
    92: ['quatre-vingt-douze', 'nonante-deux'],
    93: ['quatre-vingt-treize', 'nonante-trois'],
    94: ['quatre-vingt-quatorze', 'nonante-quatre'],
    95: ['quatre-vingt-quinze', 'nonante-cinq'],
    96: ['quatre-vingt-seize', 'nonante-six'],
    97: ['quatre-vingt-dix-sept', 'nonante-sept'],
    98: ['quatre-vingt-dix-huit', 'nonante-huit'],
    99: ['quatre-vingt-dix-neuf', 'nonante-neuf'],
    100: 'cent',
    1000: 'mille',
    1000000: 'million',
    1000000000: 'milliard',
    1000000000000: 'billion',
    1000000000000000: 'billiard',
    1000000000000000000: 'trillion',
    1000000000000000000000: 'trilliard',
    1000000000000000000000000: ['quadrillion', 'quatrillion'],
    1000000000000000000000000000: 'quadrilliard',
    1000000000000000000000000000000: 'quintillion',
    1000000000000000000000000000000000: 'quintilliard',
    1000000000000000000000000000000000000: 'sextillion',
    1000000000000000000000000000000000000000: 'sextilliard',
    1000000000000000000000000000000000000000000: 'septillion',
    1000000000000000000000000000000000000000000000: 'septilliard',
    1000000000000000000000000000000000000000000000000: 'octillion',
    1000000000000000000000000000000000000000000000000000: 'octilliard',
    1000000000000000000000000000000000000000000000000000000: 'novillion',
    1000000000000000000000000000000000000000000000000000000000:
        'novilliard',
    1000000000000000000000000000000000000000000000000000000000000:
        'décillion',
    1000000000000000000000000000000000000000000000000000000000000000:
        'décilliard',
    }

text_lookup = {}
for number, text in numeric_lookup.items():
    if type(text) in (list, tuple):
        for item in text:
            text_lookup[item] = number
    else:
        text_lookup[text] = number


def parse_number(number, determine_value=False):
    """Accepts French text representing a number which can be written, usually separated by hyphens
       :param number:             text string that may be a number
       :param determine_value:    calculate the value it represents as well
       :return: in case determine_value=True:
                 a tuple consisting of
                  * either None or the value number represents as an int or a float
                  * None:  This string cannot be converted to a valid number
                    False: This string represents a cardinal number
                    True:  This string represents an ordinal number
                in case determine_value=False:
                 a tuple consisting of
                  * True:  This string can represent a numeral
                  * False: Can't be a numeral in French"""
    result = None
    if number == '':
        result = None, None
    elif number in ['un', 'une']:
        result = 1, False

    if result:
        if determine_value:
            return result
        else:
            return not result[1] is None

    value = 0
    ordinal = False
    m = hundreds_tens_units_re.match(number)
    print(number)
    pprint(m.groupdict())

    if m:
        if m.group('ordinal'):
            ordinal = True
            if m.group('from_11_to_16_ordinal'):
                value = text_lookup[m.group('from_11_to_16_ordinal') + 'e']
            elif m.group('ordinal_30'):
                value = 30
            elif m.group('units_ordinal_5'):
                value = 5
            elif m.group('units_ordinal') == 'quatr':
                value = 4
            elif m.group('units_ordinal') == 'neuv':
                value = 9
        elif m.group('ordinal_1'):
            ordinal = True
            value = 1
        if determine_value:
            if m.group('rest'):
                try:
                    return text_lookup[m.group('rest')], False
                except:
                    try:
                        return text_lookup[m.group('rest').replace('ième', '')], True
                    except:
                        return None, None
            else:
                if m.group('from_11_to_16'):
                    value += text_lookup[m.group('from_11_to_16')]
                if m.group('tens'):
                    value += text_lookup[m.group('tens')]
                if m.group('units'):
                    if m.group('units') in ['et-un', 'et-une']:
                        value += 1
                    else:
                        value += text_lookup[m.group('units')]
                print(value, ordinal)
                return value, ordinal
        else:
            if m.group('rest'):
                return False
            else:
                return True
