import re
import stanza
from fonemas import Transcription
from dataclasses import dataclass
version = '1.0.0'  # 03/03/2023

processor_dict = {'tokenize': 'ancora', 'mwt': 'ancora', 'pos': 'ancora',
                  'ner': 'ancora', 'depparse': 'ancora'}
conf = {'lang':  'es', 'processors': processor_dict, 'download_method': 'None'}
nlp = stanza.Pipeline(**conf, logging_level='ERROR')
usuals = ('xueθ', 'suab', 'kɾuel', 'fiel', 'ruina', 'diabl', 'dios', 'kae',
          'rios', 'biɾtuos', 'kɾio', 'ʰuid', 'poɾfiad')

values = {'A': 7, 'a': 6, 'ă': 5,
          'O': 4, 'o': 3, 'ŏ': 2,
          'E': 1, 'e': 0, 'ĕ': -1,
          'I': -2, 'i': -3, 'j': -4,
          'U': -5, 'u': -6, 'w': -7,
          'y': -2, 'X': -999}
trapez = {'i': (-1, 1.25), 'e': (-0.5, 0), 'a': (0, -1.25), 'u': (1, 1.25),
          'j': (-1, 1.25), 'ĕ': (-0.5, 0), 'ă': (0, -1.25), 'w': (1, 1.25),
          'y': (-1, 1.25), 'o': (1, 0), 'ŏ': (1, 0)}
vowels, semivowels, close = 'aeiouyAEIOU', 'wjăĕŏʰ', 'iujwy'


@dataclass
class Features:
    text: str
    pos: str
    phon: list
    feats: dict
    dep: list
    ton: bool


@dataclass
class VerseFeatures:
    slbs: list
    amb: int
    count: int
    asson: str
    cons: str


class PlayLine:

    def __init__(self, line, adso=False):
        self.line = line
        self.adso = adso
        if len(line) > 0:
            self.__fixed_verse = self.__fix_line(self.__preprocess(self.line))
            self.words = self.__find_prosodic_stress(self.__fixed_verse)
        else:
            self.words = []

    def __preprocess(self, transcription):
        transcription = re.sub(r'[Pp]ara\,', 'Ppara,', transcription)
        symbols = {'(': '.', ')': '.', '—': '. ', '…': '.',  # ',': '. ',
                   ';': '.', ':': '.', '?': '.', '!': '.',
                   'õ': 'o', 'æ': 'ae',
                   'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
                   '«': '', '»': '', '–': '.', '“': '', '”': '',
                   '‘': '', '’': '', '"': '', '-': ' ', "'": ''}
        if transcription != transcription:
            transcription = 'mama mama mama mama'
        else:
            for i in symbols:
                transcription = transcription.replace(i, f'{symbols[i]} ')
            transcription = re.sub(r'\s*\.+(\w)', r',\1', transcription)
            transcription = re.sub(r'\s*\,+(\w)', r',\1', transcription)
            transcription = re.sub(r'\[|\]|¿|¡|^\s*[\.\,]', '', transcription)
            transcription = re.sub(r'\s*\.[\.\s]+', ', ', transcription)
            transcription = transcription.strip()
            # transcription = transcription[0].upper()+transcription[1:]
        verse = nlp(f'{transcription}')
        transcription = []
        for sentence in verse.sentences:
            usadas = []
            for word in sentence.words:
                if word.parent.id not in usadas:
                    usadas.append(word.parent.id)
                    word.text = word.parent.text
                    transcription.append(word)
                word.text = word.text.strip('.')
        return transcription

    def __fix_line(self, line):
        for word in line:
            words = [word for word in line if word.pos != 'X']
        while words[-1].pos == 'PUNCT':
            if any(x.isalpha() for x in words[-1].text):
                words[-1].pos = 'ADJ'
            else:
                words = words[:-1]

        if len(words) > 1:
            if words[-1].parent.text == words[-2].parent.text and \
                    words[-1].text != words[-2].text:
                words[-2].text = words[-2].parent.text
                words.pop()
        return self.__set_features(words)

    def __set_features(self, words):
        feats = []
        for word in words:
            if word.text.isalpha():
                if any(x in word.text for x in 'äëïöü'):
                    exc = 2
                else:
                    exc = 1
                feats.append(Features(word.text,
                                      word.upos,
                                      Transcription(word.text,
                                                    mono=True,
                                                    epenthesis=True,
                                                    aspiration=True,
                                                    stress='ˈ',
                                                    exceptions=exc
                                                    ).phonology.syllables,
                                      self.__parse_feats(word.feats),
                                      word.deprel,
                                      False))
        return feats

    @staticmethod
    def mark_prosodic_stress(word):
        for idx, syllable in enumerate(word.phon):
            if syllable.startswith("ˈ") or syllable.startswith("ˌ"):
                if word.ton is True:
                    syllable = syllable.translate(
                        str.maketrans("aeiou", "AEIOU"))
            word.phon[idx] = syllable.replace("ˈ", '').replace('ˌ', '').strip()
        return word

    def __fix_word(self, word):
        if word.pos == 'PUNCT' and any(x.isalpha() for x in word.text):
            word.pos = 'ADJ'
        return(word)

    def __find_prosodic_stress(self, words):
        stressed_pos = ['ADV', 'NOUN', 'PROPN',
                        'DET.Dem', 'DET.Int', 'DET.Ind', 'PRON.Com',
                        'PRON.Nom', 'PART', 'INTJ', 'ADJ', 'VERB', 'AUX']
        conjat = ['y', 'e', 'ni', 'o', 'u',
                  'que', 'quien', 'quienes',
                  'pero', 'sino', 'mas', 'aunque', 'aun'
                  'pues', 'porque', 'como', 'conque', 'si',
                  'cual', 'cuales', 'do',
                  'cuanto', 'cuanta', 'cuantos', 'cuantas',
                  'donde', 'tan',
                  'cuando', 'como',
                  'mi', 'tu', 'su', 'mis', 'tus', 'sus']
        tonicos = ['agora', 'yo', 'vos', 'es', 'soy', 'voy',
                   'sois', 'vais', 'ti', 'nosotros', 'vosotros', 'ellos',
                   'nosotras', 'vosotras', 'ellas', 'ella',
                   'todo', 'toda', 'todos', 'todas', 'cada',
                   'aqueste', 'aquesta', 'aquestos', 'aquestas',
                   'aquese', 'aquesa', 'aquesas', 'aquesos',
                   'este', 'esta', 'esto', 'estos', 'estas',
                   'ese', 'esos', 'esa', 'esas', 'eso',
                   'aquel', 'aquella', 'aquellos', 'aquellas',
                   'tuyo', 'tuyos', 'tuya', 'tuyas',
                   'suyo', 'suya', 'suyos', 'suyas']
        numbers = ['uno', 'una', 'dos', 'tres', 'cuatro', 'cinco', 'seis',
                   'siete', 'ocho', 'nueve']
        courtesy = ['don', 'doña', 'sor', 'fray',
                    'santo', 'san', 'santa', 'gran']

        PoSerrors = ['mas', 'ei']
        ant, units = '', False
        for idx, word in enumerate(words[::-1]):
            word = self.__fix_word(word)
            ton = False
            txt = word.text.lower()
            pos = word.pos
            fts = word.feats
            if idx == 0:
                ton = True
            elif txt in conjat:
                pass
            elif txt.lower() in ['oh', 'ay']:        # ADSO 100
                ant = ''
                if not self.adso:
                    ton = True
            elif any(x in txt for x in 'áéíóú'):
                ton = True
            else:
                if pos == 'NUM':
                    if ant != 'NUM':
                        ton = True
                        if txt in numbers:
                            units = True
                        else:
                            units = False
                    elif txt in numbers:
                        if units is True:
                            ton = True
                        units = True
                    else:
                        units = False
                elif txt == 'y' and ant == 'NUM':
                    pos = 'NUM'
                elif pos == 'DET':
                    nonstressed = ['me', 'te', ' le', 'nos', 'les',
                                   'lo', 'la', 'los', 'las']
                    if any(txt.endswith(x) for x in nonstressed):
                        if txt not in nonstressed:
                            ton = True
                    elif fts['PronType'] == 'Poss' or fts['Poss'] == 'Yes':
                        if txt in ['mi', 'tu', 'su', 'mis', 'tus', 'sus']:
                            pass
                        elif any([txt.startswith(x)
                                  for x in ('nuestr', 'vuestr')]):
                            if ant not in ['PROPN', 'NOUN', 'ADJ']:
                                ton = True
                        else:
                            ton = True
                    elif fts['PronType'] in ['Dem', 'Ind', 'Tot']:
                        ton = True
                    elif 'Definite' in fts:
                        if fts['Definite'] != 'Def':
                            ton = True
                elif pos in ['PROPN', 'NOUN']:
                    if not (txt.lower() in courtesy and ant == 'PROPN') and \
                            txt not in PoSerrors:
                        ton = True
                elif pos == 'ADV':
                    if txt in ('tan', 'medio', 'aun'):
                        pass
                    elif (txt in ('ya') and ant == 'SCONJ' and
                          idx + 1 != len(words)):
                        pass
                    else:
                        ton = True
                elif pos == 'PRON':
                    if txt in tonicos:
                        ton = True
                    elif any(x in txt for x in ['ar', 'er', 'ir']):
                        ton = True
                    elif txt.endswith('igo'):
                        ton = True
                    elif fts['PronType'] == 'Int,Rel':
                        pass
                    elif any(txt.startswith(x) for x in ('nuestr', 'vuestr')):
                        ton = True
                    elif 'Nom' not in fts['Case'] and \
                            fts['PronType'] == 'Prs' and \
                            txt not in ['ti', 'mí'] and fts['Poss'] != 'Yes':
                        pass
                    else:
                        ton = True
                # elif txt == 'para' and ant == 'ADV':
                #    ton = True
                elif txt in tonicos or pos in stressed_pos:
                    ton = True
            word.ton = ton
            words[idx] = self.mark_prosodic_stress(word)
            if txt not in ('y'):
                ant = pos
            else:
                ant = ''
        words.reverse()
        for idx, word in enumerate(words):
            if idx < len(words) - 1 and word.text == 'y':
                if all(x.lower() in 'aeiouwj'
                       for x in (words[idx - 1].phon[-1][-1],
                                 words[idx + 1].phon[0][0])):
                    words[idx].phon[0] = 'y'
        return [word.phon for word in words if word.pos != 'PUNCT']

    @staticmethod
    def __parse_feats(feats):
        dd = {}
        if feats:
            elements = feats.split("|")
            for element in elements:
                feature = element.split("=")
                dd[f'{feature[0]}'] = feature[1]
        else:
            dd['None'] = 'None'
        if 'Case' not in dd:
            dd['Case'] = ''
        if 'Poss' not in dd:
            dd['Poss'] = 'No'
        return dd


class VerseMetre(PlayLine):
    most_common = [6, 7, 8, 11, 10, 9, 14, 12, 5, 15, 4]

    def __init__(self, line, expected_syl=False, adso=False):
        PlayLine.__init__(self, line, adso)
        if len(self.words) > 0:
            self.synaloephas = self.__find_synaloephas(self.words)
            self.estimate, self.expected_syl = self.__adjust_expected(
                self.words, self.synaloephas, expected_syl)
            self.__verse = self.__adjust_metre(self.words, self.expected_syl)
            self.syllables = self.__verse.slbs
            self.ambiguity = self.__verse.amb
            self.asson = self.__verse.asson
            self.rhyme = self.__verse.cons
            self.count = self.__verse.count
            self.nuclei = self.find_nuclei(self.syllables)
            self.rhythm = self.find_rhyhtm(self.nuclei)
        else:
            self.synaloephas = self.syllables = self.expected_syl = []
            self.estimate = self.count = 0
            self.ambiguity = self.asson = self.rhyme = False
            self.nuclei = self.rhythm = ''

    def __find_synaloephas(self, words, h=False):
        synaloephas, ant = [], ['X']
        preference = offset = 0
        for idx, word in enumerate(words):
            # Canellada & Madsen, p. 54
            coda = word[0].replace('ʰ', '')
            onset = ant[-1]
            s = False
            if idx != 0 and all(x.lower() in vowels + semivowels
                                for x in (coda[0], onset[-1])):
                position = [idx - 1, len(words[idx - 1]) - 1]
                if idx == 1 and words[0] in (['i'], ['o'])\
                        and coda[0] in 'AEIOU':
                    preference -= 8
                if word in [[x] for x in 'ei'] and len(words) > idx + 2:
                    if onset[-1] in vowels + semivowels:
                        if not words[idx+1][0][0] in vowels + semivowels:
                            s = True
                elif all(phoneme in vowels + semivowels for phoneme in
                         [onset[-1], coda[0]]):
                    val = values[onset[-1]]
                    if len(onset) > 1 and onset[-2] in values:
                        previous_val = values[onset[-2]]
                    else:
                        previous_val = values[onset[-1]]
                    if len(coda) > 1 and coda[1] in values:
                        next_val = values[coda[1]]
                    else:
                        next_val = values[coda[0]]
                    if (previous_val <= val and val <= values[coda[0]]) or (
                                previous_val >= val and
                                val >= values[coda[0]] and
                                next_val <= values[coda[0]]) or (
                                previous_val <= val and
                                val > values[coda[0]] and
                                values[coda[0]] >= next_val):
                        s = True
            if s:
                if all(x.islower() for x in (coda[0], onset[-1])) and \
                        coda[0] == onset[-1]:
                    if any(x in (['o'], ['y']) and len(x) == 1
                           for x in (word, ant)):
                        preference -= 1
                    elif len(coda) > 1 and coda[1] in 'jwăĕŏ':
                        preference -= 2
                synaloephas.append((position,
                                    self.__synaloepha_pref(onset, coda,
                                                           preference),
                                    onset, coda))
            ant = word
            offset += len(word)
        for idx, word in enumerate(words):
            if len(word) > 1:
                preference = -12
                for idy, syllable in enumerate(word):
                    if idy > 0:
                        position = [idx, idy - 1]
                        coda = syllable
                        onset = word[idy - 1]
                        if all(x in vowels + semivowels
                               for x in [onset[-1], coda[0]]) and not (
                                   onset[-1].isupper()
                                   and idx + 1 == len(words)
                                   and idy + 1 == len(word)):
                            synaloephas.append((position,
                                                self.__synaloepha_pref(
                                                    onset, coda)
                                                + preference - 2, onset, coda))
        synaloephas.sort(key=lambda x: x[1], reverse=True)
        return synaloephas

    def __adjust_expected(self, syllables, synaloephas, expected):
        snlf = len([a for a in synaloephas if a[1] > -15])
        slbs = len(self.__flatten(syllables)) + (
            self.__find_rhyme(syllables[-1])['count'])
        slbs = slbs - snlf
        if expected:
            if expected[0] == slbs:
                exp = []
            elif expected[0] == 8:
                if slbs in (6, 7, 8, 9):
                    exp = [8]
                elif slbs < 6:
                    exp = [7, 8, 6, 5, 4, 3]
                else:
                    exp = [11]
            elif expected[0] in (7, 11):
                if slbs < 9:
                    exp = [7, 11]
                else:
                    exp = [11, 7, 8]
            elif expected[0] == 6 and slbs in (5, 6, 7):
                exp = [6, 8, 11, 7]
            else:
                exp = expected[:2] + [8, 11, 7, 6]
        else:
            expected = [6, 7, 8, 11, 10, 9, 14, 12, 5, 15, 4]
            exp = [slbs]
        return (slbs, exp + [a for a in expected if a not in exp])

    def __adjust_metre(self, syllables, expected):
        potential_synaloephas = self.__find_synaloephas(syllables)
        potential_hiatuses = self.__find_hiatuses(syllables)
        rhyme = self.__find_rhyme(syllables[-1])
        len_rhyme = len(self.__flatten(syllables)) + rhyme['count']
        offset = expected[0] - len_rhyme
        hemistich = self.__test_hemistich(syllables)
        sllbls = syllables[0:]
        if offset == 0:
            ambiguous = 0
        elif len_rhyme - len(potential_synaloephas) == expected[0]:
            ambiguous = 0
            syllables = self.__synaloephas(syllables, -offset)
        elif (len_rhyme - len(potential_synaloephas) < expected[0] and
              self.__test_hemistich(syllables) > 0):
            ambiguous = 4
            syllables = self.__resolve_long(syllables, hemistich)
            syllables = self.__synaloephas(syllables, -offset - 1)
            len_rhyme -= 1
        elif len_rhyme - len(potential_synaloephas) == expected[0]:
            ambiguous = 3
            syllables = self.__synaloephas(syllables, -offset)
        else:
            ambiguous = 1
            if offset < 0 and len(potential_synaloephas) >= -offset:
                syllables = self.__synaloephas(syllables, -offset)
            elif (len_rhyme < expected[0] > 4 and
                  len(potential_hiatuses) + len_rhyme >= expected[0]):
                expected = expected[:1] + expected
                syllables = self.__apply_hiatus(syllables,
                                                potential_hiatuses,
                                                offset)
        rhyme = self.__find_rhyme(syllables[-1])
        len_rhyme = len(self.__flatten(syllables)) + rhyme['count']
        if len_rhyme > expected[0]:
            return self.__adjust_metre(syllables, expected[1:])
        elif len_rhyme < expected[0]:
            return self.__adjust_metre(sllbls, expected[1:])
        else:
            rep = {'y': 'i', 'Y': 'I', 'ppA': 'pA'}
            for i, s in enumerate(syllables):
                if s[0] in rep.keys():
                    syllables[i][0] = rep[s[0]]
            return VerseFeatures(syllables,
                                 ambiguous,
                                 len_rhyme,
                                 rhyme['assonance'],
                                 rhyme['consonance'])

    @staticmethod
    def find_nuclei(syllables):
        vowels = 'AEIOUaeiou'
        return ''.join([nucleus for syl in [phon for clstr in
                                            syllables
                                            for phon in clstr]
                        for nucleus in syl if nucleus in vowels])

    @staticmethod
    def find_rhyhtm(syllables):
        metre = []
        for syllable in syllables:
            if any(phoneme.isupper() for phoneme in syllable):
                metre.append('+')
            else:
                metre.append('-')
        return ''.join(metre)

    # Required by __find_synaloephas
    def __synaloepha_pref(self, onset, coda, preference=0):
        distance = self.__vowel_distance(onset, coda)
        voc = vowels + semivowels + vowels.upper() + 'ʰy'
        onset = ''.join([x for x in onset if x in voc])
        coda = ''.join([x for x in coda if x in voc])
        preference -= 2*(len(onset) + len(coda) - 2 + distance)
        if coda.startswith('ʰ'):
            preference -= 2
            coda = coda.strip('ʰ')
        if coda.islower() and onset.islower():
            preference += 4
        elif any(x.islower() is False for x in (coda, onset)):
            preference -= 2
            if any(y in x for y in 'UI' for x in (coda, onset)):
                preference -= 1
            if all(x.islower() is False for x in (coda, onset)):
                preference -= 8
        if coda[0] == 'y':
            preference -= 1
        if onset[-1] == 'y':
            preference += 1
        return preference

    # Required by __adjust_metre
    @staticmethod
    def __find_hiatuses(words):
        diphthongs = []
        for idx, word in enumerate(words):
            for idy, syllable in enumerate(word):
                if re.search(r'([aeioujw])([aeioujw])([wj]*)',
                             syllable, re.IGNORECASE):
                    if idx + 1 < len(words) or idy + 1 < len(word) or \
                            not syllable.islower():
                        diphthongs.append((idx, idy))
        return diphthongs

    def __apply_hiatus(self, words, hiatuses, difference):
        sem2voc = {'j': 'i', 'w': 'u', 'J': 'I', 'W': 'U'}
        preference = self.__hiatus_preference(words, hiatuses)
        for idx in preference[:difference]:
            word = words[idx[0]]
            syllable = word[idx[1]]
            diphthong = re.search(r'([jw]*)([aeiouAEIOU])([jw]*)', syllable)
            onset = syllable.split(diphthong.group())[0]
            coda = syllable.split(diphthong.group())[1]
            semiconsonant = diphthong.group(1)
            nucleus = diphthong.group(2)
            semivowel = diphthong.group(3)
            if semivowel and nucleus:
                if nucleus.isupper():
                    nucleus, semivowel = nucleus.lower(), semivowel.upper()
                first_part = onset + nucleus
                second_part = semivowel.replace(semivowel[-1],
                                                sem2voc[semivowel[-1]]) + coda
            else:
                first_part = onset + semiconsonant.replace(
                    semiconsonant[-1], sem2voc[semiconsonant[-1]])
                second_part = nucleus + coda
            hiatus = f'{first_part} {second_part}'
            word = [(index, element) if index != idx[1] else (idx[1], hiatus)
                    for index, element in enumerate(word)]
            words[idx[0]] = re.split(' +', ' '.join([element[1]
                                                     for element in word]))
        return words

    def __test_hemistich(self, word_list):
        offset = i = correction = 0
        for idx, word in enumerate(word_list):
            if i < 4 and len(self.__flatten(word_list)) > 9:
                for idy, syllable in enumerate(word):
                    if any(x in syllable for x in 'AEIOU') and \
                            idy + offset == 3 and len(word) - idy > 2 and \
                            word[-2:] != ['mEn', 'te']:
                        correction = idx
                    i += 1
                offset += len(word)
            else:
                break
        return correction

    def __synaloephas(self, syllables, offset, count=0):
        if offset > 0:
            potential_synaloephas = self.__find_synaloephas(syllables)
            count += 1
            syllables = self.__adjust_syllables(syllables,
                                                potential_synaloephas[:1])
            return self.__synaloephas(syllables, offset-1, count)
        else:
            return syllables

    @staticmethod
    def __resolve_long(words, position):
        words[position] = words[position][:-2] + [words[position][-1]]
        return words

    @staticmethod
    def __find_rhyme(word):
        vowels, offset, tonic = 'aeiou', {-1: 1, -2: 0, -3: -1}, -1
        for idx, syllable in enumerate(word[::-1]):
            if any([phoneme.isupper() for phoneme in syllable]):
                tonic = -idx - 1
                for jdx, phoneme in enumerate(syllable):
                    if phoneme.isupper():
                        coda = word[(idx+1)*-1:]
                        coda[(idx+1)*-1] = syllable[jdx:]
                        break
                break
            else:
                coda = word[-2:]
        if tonic < -3:
            tonic = -2
        if len(coda) > 2:
            assonance = ''.join([syl.lower() for syl in [coda[i]
                                                         for i in (0, - 1)]])
        else:
            assonance = ''.join([syl.lower() for syl in coda])
        assonance = ''.join([phoneme for phoneme in assonance
                             if phoneme in vowels])
        consonance = ''.join([phoneme.lower() for phoneme in coda])
        return {'stress': tonic, 'count': offset[tonic],
                'assonance': assonance, 'consonance': consonance}

    #   Required by __synaloephas
    def __adjust_syllables(self, words, synaloephas):
        synaloephas_list = [syllable[0] for syllable in synaloephas]
        if len(synaloephas_list) < 1:
            return words
        else:
            if synaloephas_list[0][0] < sum([len(word) for word in words]):
                i_word1 = synaloephas_list[0][0]
                i_syllable1 = synaloephas_list[0][1]
                word = words[synaloephas_list[0][0]]
                l_word = len(word)
                joint = [synaloephas[0][-2], synaloephas[0][-1]]
                if i_syllable1 == l_word - 1:
                    i_syllable2 = 0
                    i_word2 = i_word1 + 1
                    if len(words[i_word1]) > 1:
                        onset = words[i_word1][:-1]
                    else:
                        onset = []
                    coda = words[i_word2][1:]
                    diphthong = [self.__apply_synaloephas(joint)]
                    word = onset + diphthong
                    if len(words[i_word2]) > 1:
                        word = word + coda
                    words = (words[:i_word1] +
                             [word] + words[i_word2+1:])
                    synaloephas_list = self.__adjust_position(
                        synaloephas_list[1:],
                        synaloephas_list[0], len(onset))
                else:
                    i_syllable2 = i_syllable1 + 1
                    onset = words[i_word1][:i_syllable1]
                    coda = words[i_word1][i_syllable2+1:]
                    diphthong = self.__apply_synaloephas(joint)
                    word = onset + [diphthong] + coda
                    words[i_word1] = word
                    synaloephas_list = self.__adjust_position(
                        synaloephas_list[1:], synaloephas_list[0], -1)
            return self.__adjust_syllables(words, synaloephas_list)

    @staticmethod
    def __apply_synaloephas(diphthong):
        diphthong[1] = diphthong[1].replace('ʰ', '')
        non_syllabic = {'a': 'ă', 'e': 'ĕ', 'i': 'j', 'o': 'ŏ', 'u': 'w',
                        'A': 'ă', 'E': 'ĕ', 'I': 'j', 'O': 'ŏ', 'U': 'w',
                        'j': 'j', 'w': 'w', 'ă': 'ă', 'ĕ': 'ĕ', 'ŏ': 'ŏ',
                        'y': 'ʝ'}
        onset, coda = diphthong[0], diphthong[1]  # .replace('ʰ', '')
        if onset[-1] == coda[0]:
            diphthong = onset[:-1] + coda
        elif onset == 'y' or (onset == 'i' and coda.startswith('u')):
            diphthong = 'ʝ' + coda
        elif values[onset[-1]] > values[coda[0]]:
            if coda[0].isupper():
                diphthong = (onset[:-1] + onset[-1].upper() +
                             non_syllabic[coda[0]] + coda[1:])
            else:
                diphthong = (onset[:-1] + onset[-1] +
                             non_syllabic[coda[0]] + coda[1:])
        else:
            if onset[-1].isupper():
                diphthong = (onset[:-1] + non_syllabic[onset[-1]] +
                             coda[0].upper() + coda[1:])
            else:
                diphthong = (onset[:-1] + non_syllabic[onset[-1]] +
                             coda[0] + coda[1:])
        return diphthong

    #   Required by __apply_hiatus
    @staticmethod
    def __hiatus_preference(words, hiatuses):
        preference = []
        for idx in hiatuses[::-1]:
            if ''.join(words[idx[0]]).lower().startswith(usuals):
                preference = [idx] + preference
            else:
                preference += [idx]
        for idx, second in enumerate(reversed(preference)):
            for first in preference[:-idx-1]:
                if first[0] == second[0] and first[1] < second[1]:
                    preference[-idx-1] = (second[0], second[1]+1)
        return preference

    # AUXILIARY METHODS
    @staticmethod
    def __flatten(thelist):
        return [item for sublist in thelist for item in sublist]

    @staticmethod
    def __vowel_distance(onset, coda):
        onset = onset.lower()
        coda = coda.strip('ʰ').lower()
        return abs(trapez[onset[-1]][0] - trapez[coda[0]][0]) + abs(
            trapez[onset[-1]][1] - trapez[coda[0]][1])

    @staticmethod
    def __adjust_position(word_list, position, offset):
        for idx, word in enumerate(word_list):
            if offset < 0:
                if word[0] == position[0]:
                    if position[1] >= position[1]:
                        word_list[idx][1] -= 1
            elif word[0] > position[0]:
                if word[0] == position[0] + 1:
                    word_list[idx][1] += offset
                word_list[idx][0] -= 1
        return word_list
