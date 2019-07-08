# coding: utf8
from __future__ import unicode_literals
import re
from pprint import pprint

wrong_ordinals_re = re.compile(r"""(?x)
.*(?P<wrong>nulste|eende|tweeste|driede|vierste|vijfste|
            zeste|zesste|zevenste|achtde|negenste|tienste|
            honderdde|duizendde)
   $""")

hundreds_units_and_tens_thousand_re = re.compile(r"""(?x)
      (
        (?P<hundreds>twee|drie|vier|vijf|zes|zeven|acht|negen)?
        (?P<hundred>honderd)
      )?
      (
        (?P<units>eenen|tweeën|drieën|vieren|vijfen|zesen|zevenen| achten|negenen)?
        (?P<tens>(      twin  |der   |veer  |vijf  |zes  |zeven  |tach   |negen)
                  tig
        )
        |
        (?P<en>en)??
        (
          (?P<from_13_to_19>(der|veer|vijf|zes|zeven|acht|negen)
                             tien
          )
          |
          (?:
            (?P<from_1_to_12>  een|twee|drie |vier|vijf|zes|
                             zeven|acht|negen|tien|elf |twaalf
            )
          )
        )
      )?
      (?P<thousand>duizend)?
      (?P<ordinal_1_12>(?P<en_ordinal>en)??
                       (?:
                         (?P<ordinal_1>eerste)
                         |
                         (?P<ordinal_3>derde)
                       )$
      )?
      (?P<ordinal>ste|de)?
      (?P<rest>.*)""")

numeric_lookup = {0: 'nul',
                  1: ['een', 'één'],
                  2: 'twee',
                  3: 'drie',
                  4: 'vier',
                  5: 'vijf',
                  6: 'zes',
                  7: 'zeven',
                  8: 'acht',
                  9: 'negen',
                  10: 'tien',
                  11: 'elf',
                  12: 'twaalf',
                  13: 'dertien',
                  14: 'veertien',
                  20: 'twintig',
                  30: 'dertig',
                  40: 'veertig',
                  50: 'vijftig',
                  60: 'zestig',
                  70: 'zeventig',
                  80: 'tachtig',
                  90: 'negentig',
                  100: 'honderd',
                  1000: 'duizend',
                  1000000: 'miljoen',
                  1000000000: 'miljard',
                  1000000000000: 'biljoen',
                  1000000000000000: 'biljard',
                  1000000000000000000: 'triljoen',
                  1000000000000000000000: 'triljard',
                  1000000000000000000000000: 'quadriljoen',
                  1000000000000000000000000000: 'quadriljard',
                  }

text_lookup = {}
for number, text in numeric_lookup.items():
    if type(text) in (list, tuple):
        for item in text:
            text_lookup[item] = number
    else:
        text_lookup[text] = number

def parse_number(number_text, determine_value=False, strict_AN_spelling=False):
    """Accepts Dutch text representing a number which can be written as a single word
       in the range of 0-999 and their multiples of 1 thousand.
       After 'duizend' a space is required
       :param number_text:             text string that may be a number
       :param determine_value:    calculate the value it represents as well
       :param strict_AN_spelling: only allow valid AN spelling
       :return: in case determine_value=True:
                 a tuple consisting of
                  * either None or the value number represents as an int or a float
                  * None:  This string cannot be converted to a valid number
                    False: This string represents a cardinal number
                    True:  This string represents an ordinal number
                in case determine_value=False:
                 a tuple consisting of
                  * True:  This string represents a numeral
                  * False: Can't be a correctly spelled numeral in Standard Dutch"""
    if ' ' in number_text:
        value = 0
        for word in number_text.split(' '):
            print(word)
            v = parse_number(word, determine_value=determine_value, strict_AN_spelling=strict_AN_spelling)
            print(v)
            if v and v[0]:
                value += v[0]
        return value, v[1]

    result = None
    if number_text == '':
        result = None, None
    elif number_text == 'driekwart':  # '3/4 is the only fraction that can be written in one word in Dutch
        result = 0.75, False
    elif number_text == 'driekwartste':  # Farfetched indeed, except maybe in Harry Potter book
        result = 0.75, True

    # First a simple check using dictionary lookup
    ordinal = False
    base = number_text
    if base.endswith('ste'):
        base = base[:-3]
        ordinal = True
    elif base.endswith('de'):
        base = base[:-2]
        ordinal = True
    if base in text_lookup:
        result = text_lookup[base], ordinal

    # But that naive approach needs to be counteracted
    # using a lightweight regex in case strict adherence to
    # AN spelling is desired.
    if strict_AN_spelling:
        test_ordinals = wrong_ordinals_re.match(number_text)
        if test_ordinals and test_ordinals.group('wrong'):
            result = None, None

    if result:
        if determine_value:
            return result
        else:
            return not result[1] is None

    # And then we can bring out the heavyweight regex
    value = 0
    m = hundreds_units_and_tens_thousand_re.match(number_text)
    pprint(m.groupdict())

    if m:
        if m.group('ordinal'):
            ordinal = True
        elif m.group('ordinal_1_12'):
            ordinal = True
            if m.group('ordinal_1'):
                value = 1
            elif m.group('ordinal_3'):
                value = 3
        else:
            ordinal = False

        if determine_value:
            if (m.group('rest') or
                (m.group('from_13_to_19') and
                 m.group('en'))):
                return None, None
            else:
                if m.group('hundreds'):
                    value += 100 * text_lookup[m.group('hundreds')]
                elif m.group('hundred'):
                    value += 100
                if m.group('from_1_to_12'):
                    value += text_lookup[m.group('from_1_to_12')]
                elif m.group('from_13_to_19'):
                    if m.group('en'):
                        return None, None
                    try:
                        value += text_lookup[m.group('from_13_to_19')]
                    except KeyError:
                        # 15 - 19
                        value += 10 + text_lookup[m.group('from_13_to_19').replace('tien', '')]
                if m.group('tens'):
                    value += text_lookup[m.group('tens')]
                if m.group('units'):
                    value += text_lookup[m.group('units')[:-2]]
                if m.group('thousand'):
                    if value:
                        value *= 1000
                    else:
                        value = 1000
                return value, ordinal
        else:
            if (m.group('rest') or
                (m.group('from_13_to_19') and
                 m.group('en'))):
                return False
            else:
                return True
