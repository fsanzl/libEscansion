# LibEscansión
> A metrical scansion library for Spanish
[![License: LGPL][license]][license-url]                                                                    
[![Version: 1.0.0][version]][version-url]
[![Python versions: 3.5, 3.6, 3.7, 3.8, 3.9][python-version]][python-version-url]

<h2 align="center">libEscansión</h2>

<h3 align="center">A Python library for for metrical scansion of mixed Spanish verses</h2>


*libEscansión* is a state-of-the-art Python library for analysing Spanish mixed verses. It parses the verse to find syllabic nuclei, rhythmic pattern, assonance, and consonance, as well as to  provide a phonological transcription of the syyllables. It scores 97.01% accuracy (99.50% discarding non-erroneous disagreements) against the manually annotated corpus [ADSO 100](/), which makes 

This library is part of the research project [Sound and Meaning in Spanish Golden Age Literature](https://soundandmeaning.univie.ac.at/). It was created as a means to gnerate a corpus of parsed metres.


## Installation

```sh
pip install libEscansion
```
## Requeriments

Following libraries are required:

* *stanza* with Spanish language models
* *fonmas*



## Usage example

The library provides the class *VerseMetre*. It accepts an obligatory string for the verse and an optional list of integers with possibles syllable-counts. This should be shorted to yield the best results.


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

## Release History

* 1.0.0
    * First public release

## Meta

Your Name – [@FerdlSanz](https://twitter.com/ferdlsanz) – fsanzl@gmail.com

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


