# DeepTranslit: Towards better transliteration for Indic languages.

**`telugu`, `kannada`, `tamil`, `malayalam`, `marathi`, `hindi` are the current supported languages.**


# Usage
**Via docker**
```bash
# Start the container in background
docker run -d -p 8080:8080 notaitech/deeptranslit:hindi
```

```python
# Query from python
import requests
requests.post('http://localhost:8080/sync', json={"data": ['mera naam amitab.']}).json()
```

**As python module**
```bash
pip install --upgrade deeptranslit
```
```python
from deeptranslit import DeepTranslit

# hindi
transliterator = DeepTranslit('hindi')
# Single sentence prediction
transliterator.transliterate('mera naam amitab.')
# [{'pred': 'मेरा नाम अमिताब.', 'prob': 0.25336900797483103}]

# Multiple sentence prediction
transliterator.transliterate(['mera naam amitab.', 'amitab-aur-abhishek'])
#[[{'pred': 'मेरा नाम अमिताब.', 'prob': 0.25336900797483103}],
# [{'pred': 'अमिताब-और-अभिषेक', 'prob': 0.1027598988040056}]]

```


# Notes:
- Tokens (characters) not present in input space (english alphabet) are copied over to output.
  - eg: (`amitab.` -> `अमिताब.`, `amitab-aur-abhishek` -> `अमिताब-और-अभिषेक`)
- Predictions are cached at word level. i.e: computationally, `transliterate('amitab amitab')` is equivalent to `transliterate('amitab')` or `transliterate('amitab amitab amitab')`
