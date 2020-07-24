# DeepTranslit: Towards better transliteration for Indic languages.

Documentation is available at http://bpraneeth.com/docs/deeptranslit

# Usage
```
from deeptranslit import DeepTranslit

transliterator = DeepTranslit('hindi')
# Currently hindi (hi) is the only supported language.

transliterator.transliterate('mai mbbs complete karliya')
[('मैं एमबीबीएस कम्प्लीट करलिया', 4), ('मैं एमबीबीएस कंप्लीट करलिया', 4), ('मैं एमबीबी कम्प्लीट करलिया', 4)]

```

# Notes:

1. The dataset is created from various sources (translation corpora (http://www.cfilt.iitb.ac.in/iitb_parallel/), wikipedia parallel titles (extracted locally using some heuristics) etc..).
2. Transliteration for low resource languages is not an easy task and will never be perfect. This module is still in beta and not perfect.

# TODO:

1. Add local caching for faster transliteration.
2. Support for more languages.
