import re
import stanza
from math import sqrt
from fonemas import Transcription
from dataclasses import dataclass
version = '1.0.0pre5'  # 5/07/2023

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
          'y': -2, 'X': -999, '': -1000}
trapez = {'i': (-1, 1), 'e': (-1, 0), 'a': (0, -1), 'u': (1, 1),
          'j': (-1, 1), 'ĕ': (-1, 0), 'ă': (0, -1), 'w': (1, 1),
          'y': (-1, 1), 'o': (1, 0), 'ŏ': (1, 0)}
non_syllabic = {'a': 'ă', 'e': 'ĕ', 'i': 'j', 'o': 'ŏ', 'u': 'w',
                'A': 'ă', 'E': 'ĕ', 'I': 'j', 'O': 'ŏ', 'U': 'w',
                'j': 'j', 'w': 'w', 'ă': 'ă', 'ĕ': 'ĕ', 'ŏ': 'ŏ',
                'y': 'ʝ'}
indeed_syllabic = {'ă': 'a', 'ĕ': 'e', 'j': 'i', 'ŏ': 'o', 'w': 'u'}
glides, close, med = 'wjăĕŏ', 'IUiuy', 'AEOaeo'
vowels, vocalic = close + med, glides + close + med
allvoc = vocalic + 'ʰ'


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
        symbols = {'(': '.', ')': '.', '—': '.', '…': '.', '‘': ' ', '’': ' ',
                   ';': '.', ':': '.', '?': '.', '!': '.', '"': ' ', '-': ' ',
                   'õ': 'o', 'æ': 'ae', 'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o',
                   'ù': 'u', '«': ' ', '»': ' ', '–': '.', '“': ' ', '”': ' ',
                   "'": ' ', '.': '. '}
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
            elif txt.lower() in ['oh', 'ay']:  # ADSO 100
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
                    if txt in ('tan', 'medio', 'aun') or (txt in 'ya' and
                                                          ant == 'SCONJ'):
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
            natural = len(self.__flatten(self.words)) + self.__find_rhyme(
                self.words[-1])['count']
            self.synaloephas = self.__find_synaloephas(self.words)
            normalsyn = [a for a in self.synaloephas if a[1] > -15]
            self.natural = natural - len(normalsyn)
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
            self.natural = 0

    def __find_synaloephas(self, words, h=False):
        synaloephas, ant = [], ['X']
        preference = offset = 0
        for idx, word in enumerate(words):
            coda = word[0].replace('ʰ', '')
            onset = ant[-1]
            s = False
            if idx != 0 and all(x.lower() in allvoc
                                for x in (coda[0], onset[-1])):
                position = [idx - 1, len(words[idx - 1]) - 1]
                if idx == 1 and words[0] in (['i'], ['o'])\
                        and coda[0] in 'AEIOU':
                    preference -= 8
                if word in [[x] for x in 'ei'] and len(words) > idx + 2:
                    if not words[idx+1][0][0] in allvoc:
                        s = True
                else:
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
                if (coda[0] + onset[-1]).islower() and coda[0] == onset[-1]:
                    if any(x in (['o'], ['y']) for x in (word, ant)):
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
                        if all(x in allvoc
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
            if expected[0] == 7:
                exp = [7, 11]
            elif expected[0] == 11:
                exp = [11, 7]
            else:
                exp = expected[:1]
        elif slbs in (6, 7, 8, 11):
            expected = [6, 7, 8, 11, 10, 9, 14, 12, 5, 15, 4]
            exp = [slbs]
        else:
            if slbs > 10:
                exp = [11]
            elif slbs > 8:
                exp = [8]
            else:
                exp = [slbs]
            expected = [8, 11, 7, 6, 10, 9, 14, 12, 5, 15, 4]
        return (slbs, exp + [a for a in expected if a not in exp])

    def __adjust_metre(self, syllables, expected):
        potential_synaloephas = self.__find_synaloephas(syllables)
        potential_hiatuses = self.__find_hiatuses(syllables)
        rhyme = self.__find_rhyme(syllables[-1])
        len_rhyme = len(self.__flatten(syllables)) + rhyme['count']
        offset = expected[0] - len_rhyme
        sllbls = syllables[0:]
        if offset == 0:
            ambiguous = 0
        elif len_rhyme - len(potential_synaloephas) == expected[0]:
            ambiguous = 0
            syllables = self.__synaloephas(syllables, -offset)
        elif len_rhyme - len(potential_synaloephas) > expected[0]:
            ambiguous = 2
            syllables = self.__synaloephas(syllables, -offset - 1)
            hemistich = self.__test_hemistich(syllables)
            if self.__test_hemistich(syllables) > 0:
                syllables = self.__resolve_long(syllables, hemistich)
                len_rhyme -= 1
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
            verse = self.__adjust_metre(sllbls, expected[1:])
        elif len_rhyme < expected[0]:
            verse = self.__adjust_metre(sllbls, expected[1:])
        else:
            rep = {'y': 'i', 'Y': 'I', 'ppA': 'pA'}
            for i, s in enumerate(syllables):
                if s[0] in rep.keys():
                    syllables[i][0] = rep[s[0]]
            verse = VerseFeatures(syllables,
                                  ambiguous,
                                  len_rhyme,
                                  rhyme['assonance'],
                                  rhyme['consonance'])
        return verse

    @staticmethod
    def find_nuclei(syllables):
        return ''.join([nucleus for syl in [phon for clstr in syllables
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

    def __synaloepha_pref(self, onset, coda, preference=0):
        distance = self.__vowel_distance(onset, coda)
        onset = ''.join([x for x in onset if x in allvoc])
        coda = ''.join([x for x in coda if x in allvoc])
        preference -= 2*(len(onset) + len(coda) - 2 + distance)
        if coda.startswith('ʰ'):
            preference -= 2
            coda = coda.strip('ʰ')
        if coda.islower() and onset.islower():
            preference += 4
        elif not (coda + onset).islower():
            preference -= 2
            if any(y in x for y in 'UI' for x in (coda, onset)):
                preference -= 1
            if (coda + onset).isupper():
                preference -= 8
        if coda[0] in 'yo':
            preference -= 1
        if onset[-1] in 'yo':
            preference += 1
        return preference

    @staticmethod
    def __find_hiatuses(words):
        diphthongs = []
        for idx, word in enumerate(words):
            ton = 0
            for idy, syllable in enumerate(reversed(word)):
                if any(x.isupper() for x in syllable):
                    ton = len(word) - idy - 1
                    continue
            for idy, syllable in enumerate(word):
                if rg := re.search(r'([wj][AEOIaeoi])|([AEOIaeoi][wj])',
                                   syllable):
                    if idy < ton or (rg.group(1) and
                                     not rg.group(1).islower()):
                        diphthongs.append((idx, idy))
        return diphthongs

    def __apply_hiatus(self, words, hiatuses, difference):
        sem2voc = {'j': 'i', 'w': 'u', 'J': 'I', 'W': 'U'}
        preference = self.__hiatus_preference(words, hiatuses)
        for idx in preference[:difference]:
            word = words[idx[0]]
            syllable = word[idx[1]]
            diphthong = re.search(r'([jw]*)([aeiouAEIOUjw])([jw]*)', syllable)
            if len(diphthong.group()) > 1:
                onset = syllable.split(diphthong.group())[0]
                coda = syllable.split(diphthong.group())[1]
                semiconsonant = diphthong.group(1)
                nucleus = diphthong.group(2)
                semivowel = diphthong.group(3)
                if semivowel and nucleus:
                    if nucleus.isupper():
                        nucleus, semivowel = nucleus.lower(), semivowel.upper()
                    first = onset + nucleus
                    second = semivowel.replace(semivowel[-1],
                                               sem2voc[semivowel[-1]]) + coda
                else:
                    first = onset + semiconsonant.replace(
                        semiconsonant[-1], sem2voc[semiconsonant[-1]])
                    second = nucleus + coda
                hiatus = f'{first} {second}'
                word = [(index, element) if index != idx[1] else
                        (idx[1], hiatus) for index, element in enumerate(word)]
                words[idx[0]] = re.split(' +', ' '.join([element[1]
                                                         for element in word]))
        return words

    def __test_hemistich(self, word_list):
        offset = i = correction = 0
        for idx, word in enumerate(word_list):
            if len(self.__flatten(word_list)) > 9:
                for idy, syllable in enumerate(word):
                    if any(x in syllable for x in 'AEIOU') \
                            and idy + offset in (3, 5):
                        if len(word) - idy > 2 and word[-2:] != ['mEn', 'te']:
                            correction = idx
                        break
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
            syllables = self.__synaloephas(syllables, offset-1, count)
        return syllables

    @staticmethod
    def __resolve_long(words, position):
        words[position] = words[position][:-2] + [words[position][-1]]
        return words

    @staticmethod
    def __find_rhyme(word):
        offset, tonic = {-1: 1, -2: 0, -3: -1}, -1
        for idx, syllable in enumerate(word[::-1]):
            if not syllable.islower():
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
                                                         for i in (0, -1)]])
        else:
            assonance = ''.join([syl.lower() for syl in coda])
        assonance = ''.join([phoneme for phoneme in assonance
                             if phoneme in vowels])
        consonance = ''.join([phoneme.lower() for phoneme in coda])
        return {'stress': tonic, 'count': offset[tonic],
                'assonance': assonance, 'consonance': consonance}

    def __adjust_syllables(self, words, synaloephas):
        synaloephas_list = [syllable[0] for syllable in synaloephas]
        if synaloephas_list:
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
                words = (words[:i_word1] + [word] + words[i_word2+1:])
                synaloephas_list = self.__adjust_position(
                    synaloephas_list[1:], synaloephas_list[0], len(onset))
            else:
                i_syllable2 = i_syllable1 + 1
                onset = words[i_word1][:i_syllable1]
                coda = words[i_word1][i_syllable2+1:]
                diphthong = self.__apply_synaloephas(joint)
                word = onset + [diphthong] + coda
                words[i_word1] = word
                synaloephas_list = self.__adjust_position(
                    synaloephas_list[1:], synaloephas_list[0], -1)
            words = self.__adjust_syllables(words, synaloephas_list)
        return words

    @staticmethod
    def __perception(chain, may=False):
        max = -999
        for x in chain:
            if x in non_syllabic and values[x] > max:
                max = values[x]
        chain = list(chain)
        for i, x in enumerate(chain):
            if x in non_syllabic:
                if values[x] < max:
                    chain[i] = non_syllabic[x]
                else:
                    chain[i] = indeed_syllabic[x]
        chain = ''.join(chain)
        if may:
            for j in 'aeo':
                chain = chain.replace(j, j.upper())
        return chain

    def __apply_synaloephas(self, diphthong):
        diphthong[1] = diphthong[1].replace('ʰ', '')
        onset, coda = diphthong[0], diphthong[1]
        onsetb = ''.join([non_syllabic[x] if x in non_syllabic else x
                          for x in onset])
        codab = ''.join([non_syllabic[x] if x in non_syllabic else x
                         for x in coda])
        if non_syllabic[onset[-1]] == non_syllabic[coda[0]]:
            if coda[0] in glides or onset[-1].isupper():
                diphthong = onset + coda[1:]
            else:
                diphthong = onset[:-1] + coda
        elif len([x for x in onset + coda if x in non_syllabic]) > 2:
            tonic = not (onset + coda).islower()
            diphthong = self.__perception(onsetb + codab.replace('ʝ', 'j'),
                                          tonic)
        elif onset == 'y' or (onset == 'i' and coda.startswith('u')):
            diphthong = 'ʝ' + coda
        elif not onset.islower() and (coda.islower() or
                                      values[onset[-1]] > values[coda[0]]):
            diphthong = onset + codab.replace('ʝ', 'j')
        else:
            diphthong = onsetb + coda
        return diphthong

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

    @staticmethod
    def __flatten(thelist):
        return [item for sublist in thelist for item in sublist]

    @staticmethod
    def __vowel_distance(onset, coda):
        onset = onset.lower()
        coda = coda.strip('ʰ').lower()
        distance = sqrt(pow(abs(trapez[onset[-1]][0] - trapez[coda[0]][0]), 2)
                        + pow(abs(trapez[onset[-1]][1] -
                                  trapez[coda[0]][1]), 2))
        return distance

    @staticmethod
    def __adjust_position(word_list, position, offset):
        for idx, word in enumerate(word_list):
            if offset < 0:
                if word[0] == position[0]:
                    if word[1] >= position[1]:
                        word_list[idx][1] -= 1
            elif word[0] > position[0]:
                if word[0] == position[0] + 1:
                    word_list[idx][1] += offset
                word_list[idx][0] -= 1
        return word_list
