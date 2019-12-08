import os
import re
import pickle
import string
import pydload
import logging
import itertools

from txt2txt import infer, build_model

kenlm_available = True

try:
    import kenlm
except:
    logging.warn('KenLm not installed. Simple scoring will be used.')
    kenlm_available = False

model_links = {
            'hi': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_hi_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_hi_params',
                    'words': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/hi_words',
                    'lm': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/hi_lm.bin'
                },
            }

lang_code_mapping = {
            'hindi': 'hi',
        }

class DeepTranslit():
    params = None
    model = None
    words = None
    lm = None
    rank = 'auto'

    def __init__(self, lang_code, rank='auto'):
        if lang_code in lang_code_mapping:
            lang_code = lang_code_mapping[lang_code]
        
        if lang_code not in model_links:
            print("DeepTranslit doesn't support '" + lang_code + "' yet.")
            print("Please raise a issue at https://github.com/bedapudi6788/deeptranslit to add this language into future checklist.")
            return None
        
        # loading the model
        home = os.path.expanduser("~")
        lang_path = os.path.join(home, '.DeepTranslit_' + lang_code)
        checkpoint_path = os.path.join(lang_path, 'checkpoint')
        params_path = os.path.join(lang_path, 'params')
        words_path = os.path.join(lang_path, 'words')
        lm_path = os.path.join(lang_path, 'lm')
        
        if not os.path.exists(lang_path):
            os.mkdir(lang_path)

        if not os.path.exists(checkpoint_path):
            print('Downloading checkpoint', model_links[lang_code]['checkpoint'], 'to', checkpoint_path)
            pydload.dload(url=model_links[lang_code]['checkpoint'], save_to_path=checkpoint_path, max_time=None)

        if not os.path.exists(params_path):
            print('Downloading model params', model_links[lang_code]['params'], 'to', params_path)
            pydload.dload(url=model_links[lang_code]['params'], save_to_path=params_path, max_time=None)
        
        if not os.path.exists(words_path):
            print('Downloading words', model_links[lang_code]['words'], 'to', words_path)
            pydload.dload(url=model_links[lang_code]['words'], save_to_path=words_path, max_time=None)

        if not os.path.exists(lm_path):
            print('Downloading lm', model_links[lang_code]['lm'], 'to', lm_path)
            pydload.dload(url=model_links[lang_code]['lm'], save_to_path=lm_path, max_time=None)
        
        DeepTranslit.model, DeepTranslit.params = build_model(params_path=params_path, enc_lstm_units=64, use_gru=True, display_summary=False)
        DeepTranslit.model.load_weights(checkpoint_path)

        DeepTranslit.words = pickle.load(open(words_path, 'rb'))

        if kenlm_available and rank in {'auto', 'kenlm'}:
            logging.warn('Loading KenLM.')
            DeepTranslit.lm = kenlm.Model(lm_path)
            DeepTranslit.rank = rank

    def transliterate(self, sent, top=3):
        rank = DeepTranslit.rank
        words = sent.strip().split()
        puncs = []
        for i, word in enumerate(words):
            words[i] = re.sub('[' + string.punctuation + ']', '', word.lower())
            if not words[i]:
                continue

            punc = None
            if word[-1] in string.punctuation:
                punc = word[-1]
            
            puncs.append(punc)

        words = [w for w in words if w]
        
        np_words = []

        for i, word in enumerate(words):
            if [c for c in word if c not in DeepTranslit.params['input_encoding']]:
                np_words.append((i - len(np_words), word))
                words[i] = None
            
        words = [w for w in words if w]        

        preds = infer(words, DeepTranslit.model, DeepTranslit.params)

        for posi, np_word in np_words:
            preds = preds[:posi] + [[{'sequence': np_word, 'prob': 1}]] + preds[posi:]

        resp = []

        preds = list(itertools.product(*preds))

        for pred in preds:
            words = [w['sequence'] for w in pred]
            for i, word in enumerate(words):
                if puncs[i]:
                    word = word + puncs[i]
                words[i] = word

            probs = [w['prob'] for w in pred]

            sent = ' '.join(words)
            resp.append((sent, probs))
        
        if rank == 'auto':
            if kenlm_available:
                rank = 'kenlm'
            else:
                rank = 'simple'

        if rank == 'simple':
            for i, (sent, probs) in enumerate(resp):
                words = sent.split()
                score = sum([1 for word in words if word in DeepTranslit.words])
                resp[i] = (sent, score)
            
            resp = sorted(resp, key=lambda x: x[1], reverse=True)
        
        elif rank == 'kenlm':
            if not kenlm_available:
                logging.error("KenLm not available")
                return resp

            for i, (sent, probs) in enumerate(resp):
                score = DeepTranslit.lm.score(sent)
                resp[i] = (sent, score)

            resp = sorted(resp, key=lambda x: x[1], reverse=True) 
        

        if top:
            resp = resp[:top]

        return resp
