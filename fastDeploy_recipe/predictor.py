from deeptranslit import DeepTranslit

import os

transliterator = DeepTranslit(os.getenv("LANG", "hindi"))

TOP_N = int(os.getenv('TOP_N', '1'))

cache = {}

def predictor(in_sents=[], batch_size=1):
    if not in_sents:
        return in_sents
    
    return transliterator.transliterate(in_sents, top_n=TOP_N)

if __name__ == '__main__':
    import json
    import pickle

    example = [
        "praneeth"
    ]

    print(json.dumps(predictor(example)))

    pickle.dump(example, open("example.pkl", "wb"), protocol=2)
