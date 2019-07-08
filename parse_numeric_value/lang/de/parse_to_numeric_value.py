# coding: utf8
from __future__ import unicode_literals
import re
# from pprint import pprint


wrong_ordinals_re = re.compile(r"""(?x)
.*(?P<wrong>einte|dreite|siebente|achtte)
   $""")

hundreds_units_and_tens_thousand_re = re.compile(r"""(?x)
      (
        (?P<hundreds>zwei|drei|vier|fünf|sechs|sieben|acht|neun)?
        (?P<hundred>hundert)
      )*
      (
        (?:
          (?P<units>ein|zwei|drei|vier|fünf|sechs|sieben|acht|neun)?
                    und
        )?
        (?P<tens>(zwan|drei|vier|fünf|sech|sieb|acht|neun)
                  zig
        )
        |
        (
          (?P<from_13_to_19>(drei|vier|fünf|sech|sieb|acht|neun)
                             zehn
          )
          |
          (?:
            (?P<from_1_to_12>   ein|zwei|drei|vier|fünf|sechs|
                             sieben|acht|neun|zehn|elf |zwölf
            )
          )
        )
      )*
      (?P<thousand>tausend)?
      (?P<ordinal_1_3_7_8>
                       (?:
                         (?P<ordinal_1>erste[rs]?)
                         |
                         (?P<ordinal_3>dritte[rs]?)
                         |
                         (?P<ordinal_7>siebte[rs]?)
                         |
                         (?P<ordinal_8>achte[rs]?)
                       )$
      )?
      (?P<ordinal>[s]?te[?P<ordinal_gender>rs]?)?
      (?P<rest>.*)""")

numeric_lookup = {0: 'null',
                  1: ['ein', 'eins'],
                  2: 'zwei',
                  3: 'drei',
                  4: 'vier',
                  5: 'fünf',
                  6: 'sechs',
                  7: 'sieben',
                  8: 'acht',
                  9: 'neun',
                  10: 'zehn',
                  11: 'elf',
                  12: 'zwölf',
                  16: 'sechzehn',
                  17: 'siebzehn',
                  20: 'zwanzig',
                  30: 'dreizig',
                  40: 'vierzig',
                  50: 'fünfzig',
                  60: 'sechzig',
                  70: 'siebzig',
                  80: 'achtzig',
                  90: 'neunzig',
                  100: 'hundert',
                  101: ['hundertein', 'hunderteins'],
                  1000: 'tausend',
                  1001: ['tausendein', 'tausendeins'],
                  1000000: 'million',
                  1000000000: 'milliarde',
                  1000000000000: 'billion',
                  1000000000000000: 'billiarde',
                  1000000000000000000: 'trillion',
                  1000000000000000000000: 'trilliarde',
                  1000000000000000000000000: 'quadrillion',
                  1000000000000000000000000000: 'quadrilliarde',
                  }

text_lookup = {}
for number, text in numeric_lookup.items():
    if type(text) in (list, tuple):
        for item in text:
            text_lookup[item] = number
    else:
        text_lookup[text] = number


def parse_number(number, determine_value=False):
    """Accepts German text representing a number which can be written as a single word
       in the range of 0-999 and their multiples of 1 thousand.
       After 'tausend' a space is required
       :param number: text string that may be a number
       :param determine_value: calculate the value number represents as well
       :return: if determine_value: a tuple consisting of
                  * either None or the value number represents as an int or a float
                  * None:  This string cannot be converted to a valid number
                    False: This string represents a cardinal number
                    True:  This string represents an ordinal number
                otherwise a boolean
                  * True:  This string represents a numeral
                  * False: Can't be a correctly spelled numeral in German"""
    result = None
    if number == '':
        result = None, None
    elif number == 'eins':
        result = 1, False

    # First a simple check using dictionary lookup
    ordinal = False
    base = number
    if base.endswith('ste'):
        base = base[:-3]
        ordinal = True
    elif base.endswith('te'):
        base = base[:-2]
        ordinal = True
    if base in text_lookup:
        result = text_lookup[base], ordinal

    # But that naive approach needs to be counteracted
    # using a lightweight regex
    test_ordinals = wrong_ordinals_re.match(number)
    if test_ordinals and test_ordinals.group('wrong'):
        result = None, None

    if result:
        if determine_value:
            return result
        else:
            return not result[1] is None

    # And then we can bring out the heavyweight regex
    value = 0
    m = hundreds_units_and_tens_thousand_re.match(number)
    if m:
        if m.group('ordinal'):
            ordinal = True
        elif m.group('ordinal_1_3_7_8'):
            ordinal = True
            if m.group('ordinal_1'):
                value = 1
            elif m.group('ordinal_3'):
                value = 3
            elif m.group('ordinal_7'):
                value = 7
            elif m.group('ordinal_8'):
                value = 8
        else:
            ordinal = False

        if determine_value:
            if m.group('rest'):
                return None, None
            else:
                if m.group('hundreds'):
                    value += 100 * text_lookup[m.group('hundreds')]
                elif m.group('hundred'):
                    value += 100
                if m.group('from_1_to_12'):
                    value += text_lookup[m.group('from_1_to_12')]
                elif m.group('from_13_to_19'):
                    try:
                        value += text_lookup[m.group('from_13_to_19')]
                    except KeyError:
                        # 15 - 19
                        value += 10 + text_lookup[m.group('from_13_to_19').replace('zehn', '')]
                if m.group('tens'):
                    value += text_lookup[m.group('tens')]
                if m.group('units'):
                    value += text_lookup[m.group('units')]
                if m.group('thousand'):
                    if value:
                        value *= 1000
                    else:
                        value = 1000
                return value, ordinal
        else:
            if m.group('rest'):
                return False
            else:
                return True

