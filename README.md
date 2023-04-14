# LibEscansión
> A metrical scansion library for Spanish
[![License: LGPL](https://img.shields.io/github/license/fsanzl/fonemas)](https://opensource.org/licenses/LGPL-2.1)
[![Version: 1.0.0](https://img.shields.io/github/v/release/fsanzl/fonemas)](https://github.com/fsanzl/libEscansion/releases/tag/1.0.0)
[![Python versions: 3.9](https://img.shields.io/pypi/pyversions/fonemas)](https://www.python.org/downloads/release/python-390/)

<h2 align="center">libEscansión</h2>

<h3 align="center">A Python library for for metrical scansion of mixed Spanish verses</h2>


*libEscansión* is a state-of-the-art Python library for analysing Spanish mixed verses. It parses the verse to find syllabic nuclei, rhythmic pattern, assonance, and consonance, as well as to  provide a phonological transcription of the syyllables. It scores 98.64% accuracy against the manually annotated corpus [ADSO 100] with the option *adso=True*, which forces considering interjections as non-stressed to meet ADSO's criteria. This tops the until-now state-of-the-art. Nevertheless, vanilla scansion still outperforms the state-of-the art as it achieves 96.8%. Furthermore, after evaluating the corpus' manual scansion and spelling, we found that the disagreement was in most cases due to an improper spelling or even to non-standard human  analysis (unstressed interjections, adverbd in -mente lacking secondary stress, etc.). With a corrected corpus, the agreement reaches 99.13 %, being the resting 0.87% non-erroneus disagreements.

This library is part of the research project [Sound and Meaning in Spanish Golden Age Literature](https://soundandmeaning.univie.ac.at/). It was created as a means to generate a corpus of parsed metres, which is publicicily accessible [here](https://soundandmeaning.univie.ac.at/?page_id=175)


## Installation

```sh
pip install libEscansion
```

Alternatively, the lasr 
## Requeriments

Following libraries are required:

* *stanza* >= 1.4.2 with Spanish language models
* *fonemas* >= 2.0.16



## Usage example

The library provides the class *VerseMetre*. It accepts an obligatory string for the verse and an optional list of integers with possibles syllable-counts. If a second argment is not provided, it performs a regular scansion, i.e., with all natural dialoephas.


```python                                                                                                                                                                                      
>>> import libEscansion
>>> verse = verse = libscansion.VerseMetre('Cerrar podrá mis ojos la postrera ', [11,8,7])
>>> verse.count 
11
>>> verse.syllables
['θe', 'rAɾ', 'po', 'dɾA', 'mis', 'O', 'xos', 'la', 'pos', 'tɾE', 'ɾa']
>>> verse.nuclei  
'eAoAiOoaoEa'
>>> verse.rhyme
'eɾa'
>>> verse.asson
'ea'
>>> verse.rhythm  
'-+-+-+---+-'
```
The directory 'utils' contains a file that can be used to test the library against ADSO 100 (or any other corpus of sonnets whasoever as long as they are encoded as XML-TEI with their metres are annotated). In the same directory containing the XML files, type:

```bash
./adso100test.py *xml
```

## Release History


### 1.0.0pre1
- First public release

## Meta

Fernando Sanz-Lázaro – [@FerdlSanz](https://twitter.com/ferdlsanz) – fsanzl@gmail.com

Distributed under the LGPL 2.1 license. See ``LICENSE`` for more information.

[https://github.com/fsanzl/libEscansion](https://github.com/dbader/)

## Contributing

1. Fork it (<https://github.com/fsanzl/libEscansion/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## References

ADSO 100: Navarro-Colorado, Borja; Ribes Lafoz, María, and Sánchez, Noelia (2015) "Metrical annotation of a large corpus of Spanish sonnets: representation, scansion and evaluation" 10th edition of the Language Resources and Evaluation Conference 2016 Portorož, Slovenia. ([PDF](http://www.dlsi.ua.es/~borja/navarro2016_MetricalPatternsBank.pdf))


<!-- Markdown link & img dfn's -->
[license]: https://img.shields.io/github/license/fsanzl/libEscansion
[license-url]: https://opensource.org/licenses/LGPL-2.1
[version]: https://img.shields.io/github/v/release/fsanzl/libEscansion
[version-url]: https://pypi.org/project/libEscansion/
[python-version]: https://img.shields.io/pypi/pyversions/libEscansion
[python-version-url]: https://pypi.org/project/libEscansion/
[wiki]: https://github.com/yourname/yourproject/wiki


