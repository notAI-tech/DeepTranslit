import os
import re
import numpy
import pickle
import string
import pydload
import logging
import itertools
from txt2txt import infer, build_model

model_links = {
            'hin': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_hi_checkpoint_v2',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_hi_params_v2',
                },
            'tel': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_te_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_te_params',
                },
            'kan': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_ka_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_ka_params',
                },
            'mal': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_mal_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_mal_params',
                },
            'mar': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_mar_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_mar_params',
                },
            'tam': {
                    'checkpoint': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_ta_checkpoint',
                    'params': 'https://github.com/bedapudi6788/DeepTranslit/releases/download/v0.5/en_ta_params',
                },
            }

lang_code_mapping = {
            'hindi': 'hin',
            'telugu': 'tel',
            'kannada': 'kan',
            'malayalam': 'mal',
            'marathi': 'mar',
            'tamil': 'tam'
        }


def tokenize(word, alphabet=set('qwertyuiopasdfghjklzxcvbnm'), preprocess=True):
    if preprocess:
        word = word.strip().lower() 
    return ''.join([c if c in alphabet else ' ' + c + ' ' for c in word]).strip().split()

class DeepTranslit():
    params = None
    model = None
    cache = {}

    def __init__(self, lang_code):
        """
        Initialize deeptranslit

        Parameters:

        lang_code (str): Name or code of the language. (Currently supported: hindi/hi)

        """

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
        
        if not os.path.exists(lang_path):
            os.mkdir(lang_path)

        if not os.path.exists(checkpoint_path):
            print('Downloading checkpoint', model_links[lang_code]['checkpoint'], 'to', checkpoint_path)
            pydload.dload(url=model_links[lang_code]['checkpoint'], save_to_path=checkpoint_path, max_time=None)

        if not os.path.exists(params_path):
            print('Downloading model params', model_links[lang_code]['params'], 'to', params_path)
            pydload.dload(url=model_links[lang_code]['params'], save_to_path=params_path, max_time=None)
        
        self.model, self.params = build_model(params_path=params_path, enc_lstm_units=64, use_gru=True, display_summary=False)
        self.model.load_weights(checkpoint_path)


    def transliterate_words(self, in_words, top_n=1):
        """
        Transliterate an input word while preserving unknown tokens.

        Parameters:

        sent (str): word(s) to be transliterated.

        top (int): top-n results to be returned. | also the beam size

        Returns:

        list: returns list of dicts eg: [{'pred': string, 'prob': float}, {'pred': string, 'prob': float}, ..] per each input.

        """
        return_single = False
        if not isinstance(in_words, list):
            return_single = True
            in_words = [in_words]

        orig_to_tokenized_map = {}
        for in_word in in_words:
            orig_to_tokenized_map[in_word] = tokenize(in_word, alphabet=self.params['input_encoding'], preprocess=True)
        
        unique_tokens = set()
        for in_word, tokens in orig_to_tokenized_map.items():
            for token in tokens:
                if [c for c in token if c not in self.params['input_encoding']] or token in self.cache:
                    continue

                unique_tokens.add(token)
        
        unique_tokens = list(unique_tokens)

        if unique_tokens:
            unique_token_preds = infer(unique_tokens, self.model, self.params, max_beams=top_n, cut_off_ratio=2)
            self.cache.update({token: token_pred for token, token_pred in zip(unique_tokens, unique_token_preds)})

        all_preds = []

        for in_word in in_words:
            if in_word not in orig_to_tokenized_map:
                all_preds.append([{'pred': in_word, 'prob': 1}])
            else:
                preds = itertools.product(*[self.cache.get(token, [{'sequence': token, 'prob': 1}]) for token in orig_to_tokenized_map[in_word]])
                preds = [{'pred': ''.join([p['sequence'] for p in pred]), 'prob': numpy.prod([p['prob'] for p in pred])} for pred in preds]
                preds = sorted(preds, key=lambda x: x['prob'], reverse=True)[:top_n]
                all_preds.append(preds)
        
        if return_single:
            all_preds = all_preds[0]

        return all_preds
                    

    def transliterate(self, sents, top_n=1):
        """
        Transliterate an input sentence while preserving unknown tokens.

        Parameters:

        sent (str): Sentence(s) to be transliterated.

        top (int): top-n results to be returned. | also the beam size

        Returns:

        list: returns list of dicts eg: [{'pred': string, 'prob': float}, {'pred': string, 'prob': float}, ..] per each input.

        """
        return_single = False
        if not isinstance(sents, list):
            return_single = True
            sents = [sents]

        sents = [' '.join(sent.strip().split()) for sent in sents]

        all_unique_words = list(set(' '.join(sents).split()))
        word_preds = self.transliterate_words(all_unique_words, top_n=top_n)
        word_preds = {w: p for w, p in zip(all_unique_words, word_preds)}

        sent_preds = []

        for sent in sents:
            preds = itertools.product(*[word_preds.get(w, [{'pred': w, 'prob': 1}]) for w in sent.split()])
            preds = [{'pred': ' '.join([p['pred'] for p in pred]), 'prob': numpy.prod([p['prob'] for p in pred])} for pred in preds]
            preds = sorted(preds, key=lambda x: x['prob'], reverse=True)[:top_n]
            sent_preds.append(preds)

        if return_single:
            sent_preds = sent_preds[0]

        return sent_preds

