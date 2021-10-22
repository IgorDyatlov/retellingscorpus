#!/usr/bin/env python
# coding: utf-8

# In[3]:


import json
import pymorphy2


# In[4]:


morph = pymorphy2.MorphAnalyzer()


# In[5]:


with open("retellingscorpus/retellings_corpus.json", encoding="utf-8") as f:
    corpus = json.load(f)


# In[6]:


pos_translation = {"INFN": ['VERB'],
                  "GRND": ['VERB'],
                  "PRTS": ['VERB', 'PRT', 'ADJ'],
                  "PRTF": ['VERB', 'PRT', 'ADJ'],
                  "ADJS": ['ADJ'],
                  "ADJF": ['ADJ']}


# In[7]:


all_lemmas = dict()
all_words = dict()
all_POS = dict()
for text in range(len(corpus['corpus'])):
    for sentence in range(len(corpus['corpus'][text]['sentences'])):
        for wordform in range(len(corpus['corpus'][text]['sentences'][sentence]['tokens'])):
            k = corpus['corpus'][text]['sentences'][sentence]['tokens'][wordform] # list of [word, lemma, POS]
            word = k[0]
            lemma = k[1]
            pos = k[2]
            
            if word in all_words.keys():
                if text in all_words[word].keys():
                    if sentence in all_words[word][text].keys():
                        all_words[word][text][sentence] += [wordform]
                    else:
                        all_words[word][text][sentence] = [wordform]
                else:
                    all_words[word][text] = {sentence:[wordform]}
            else:
                all_words[word] = {text:{sentence:[wordform]}}
                
                
            if lemma in all_lemmas.keys():
                if text in all_lemmas[lemma].keys():
                    if sentence in all_lemmas[lemma][text].keys():
                        all_lemmas[lemma][text][sentence] += [wordform]
                    else:
                        all_lemmas[lemma][text][sentence] = [wordform]
                else:
                    all_lemmas[lemma][text] = {sentence:[wordform]}
            else:
                all_lemmas[lemma] = {text:{sentence:[wordform]}}
                
                
            if pos in all_POS.keys():
                if text in all_POS[pos].keys():
                    if sentence in all_POS[pos][text].keys():
                        all_POS[pos][text][sentence] += [wordform]
                    else:
                        all_POS[pos][text][sentence] = [wordform]
                else:
                    all_POS[pos][text] = {sentence:[wordform]}
            else:
                all_POS[pos] = {text:{sentence:[wordform]}}
            
            if pos in pos_translation.keys():
                tags = pos_translation[pos]
                for tag in tags:
                    if tag in all_POS:
                        if text in all_POS[tag].keys():
                            if sentence in all_POS[tag][text].keys():
                                all_POS[tag][text][sentence] += [wordform]
                            else:
                                all_POS[tag][text][sentence] = [wordform]
                        else:
                            all_POS[tag][text] = {sentence:[wordform]}
                    else:
                        all_POS[tag] = {text:{sentence:[wordform]}}


# In[8]:


def single_word_search(keyword):
    keyword = keyword.lower()
    result = []
    if "+" not in keyword:
        if keyword.upper() in all_POS.keys():
            #поиск по части речи
                reviews = all_POS[keyword.upper()].keys()
                for review in reviews:
                    result += [tuple([corpus['corpus'][review], all_POS[keyword.upper()][review]])]
        elif '"' not in keyword:
            #поиск по лемме
            keyword = morph.parse(keyword)[0].normal_form
            if keyword in all_lemmas.keys():
                reviews = all_lemmas[keyword].keys()
                for review in reviews:
                    result += [tuple([corpus['corpus'][review], all_lemmas[keyword][review]])]
        elif keyword.startswith('"') and keyword.endswith('"'):
            # поиск по словоформе
            keyword = keyword.strip('"')
            if keyword:
                if keyword in all_words.keys():
                    reviews = all_words[keyword].keys()
                    for review in reviews:
                        result += [tuple([corpus['corpus'][review], all_words[keyword][review]])]
            else:
                return 'Пожалуйста, введите непустой запрос'
        else:
            return 'Для поиска по точной словоформе введите слово в кавычках'
    else:
        #поиск по слово+частеречный_тег
        kw = keyword.split('+')
        if len(kw) != 2:
            return 'Пожалуйста, введите запрос в формате слово+ТЕГ'
        else:
            keyword, kwpos = kw[0], kw[1]
            keyword = morph.parse(keyword)[0].normal_form
            if kwpos.upper() in all_POS.keys() and keyword in all_lemmas.keys():
                pos_locations = all_POS[kwpos.upper()]
                word_locations = all_lemmas[keyword]
                pos_texts = set(pos_locations.keys())
                word_texts = set(word_locations.keys())
                pos_and_word_texts = pos_texts & word_texts # indices of texts where both POS and word occur
                for text in pos_and_word_texts:
                    to_add = {}
                    word_sent = set(word_locations[text].keys())
                    pos_sent = set(pos_locations[text].keys())
                    p_a_w_sents = word_sent & pos_sent
                    
                    for sent in p_a_w_sents:
                        pos_ind = pos_locations[text][sent]
                        word_ind = word_locations[text][sent]
                        p_a_w_ind = set(pos_ind) & set(word_ind)
                        if p_a_w_ind:
                            to_add[sent] = tuple(p_a_w_ind)
                    if to_add:
                        result += [tuple([corpus['corpus'][text], to_add])]
                    
                    
    return result


# In[284]:


def collocation_search(keywords):
    first_word = keywords[0]
    first_result = single_word_search(first_word)
    if type(first_result) != type([]):
        return first_result
    result = []
    for occurrence in first_result:
        to_add = dict()
        review = occurrence[0]
        indices = occurrence[1]
        sents = indices.keys()
        for sent in sents:
            full_sent = review['sentences'][sent]
            word_ind = indices[sent]
            for ind in word_ind:
                if len(keywords) <= len(full_sent['tokens'])-ind:
                    f = True
                    next_ind = ind
                    for keyword in keywords[1:]:
                        keyword = keyword.lower()                   
                        if f:
                            next_ind += 1
                            token = full_sent['tokens'][next_ind]
                            token_w = token[0]
                            token_l = token[1]
                            token_p = token[2].strip()
                            if "+" not in keyword:
                                if keyword.upper() in all_POS.keys():
                                #поиск по части речи
                                    if (keyword.upper() == "ADJ") and (token_p not in ['ADJS', 'ADJF', 'PRTF', 'PRTS']):
                                        f = False
                                    elif (keyword.upper() == "PRT") and (token_p not in ['PRTS', 'PRTF']):
                                        f = False
                                    elif (keyword.upper() == "VERB") and (token_p not in ['VERB', 'PRTF', 'PRTS', 'GRND', 'INFN', 'PRED']):
                                        f = False
                                    elif keyword.upper() not in ["ADJ", "PRT"] and token_p != keyword.upper():
                                        f = False
                
                                elif '"' not in keyword:
                                    keyword = morph.parse(keyword)[0].normal_form
                                    if token_l != keyword:
                                        f = False
                                        
                                elif keyword.startswith('"') and keyword.endswith('"'):
                                    keyword = keyword.strip('"')
                                    if keyword:
                                        if keyword != token_w:
                                            f = False
                                    else:
                                        return 'Пожалуйста, введите слово в кавычках'
                                else:
                                    return 'Пожалуйста, введите слово в кавычках'
                                
                            else:
                                kw = keyword.split('+')
                                if len(kw) != 2:
                                    return 'Пожалуйста, введите запрос в формате слово+ТЕГ'
                                else:
                                    keyword, kwpos = kw[0], kw[1]
                                    keyword = morph.parse(keyword)[0].normal_form
                                    if token_l == keyword:
                                        if kwpos.upper() == "ADJ" and token_p not in ['ADJS', 'ADJF', 'PRTF', 'PRTS']:
                                            f = False
                                        elif kwpos.upper() == "PRT" and token_p not in ['VERB', 'PRTF', 'PRTS', 'GRND', 'INFN', 'PRED']:
                                            f = False
                                        elif kwpos.upper() == "VERB" and token_p not in ['VERB', 'PRTF', 'PRTS', 'GRND', 'INFN', 'PRED']:
                                            f = False
                                        elif kwpos.upper() not in ["ADJ", "PRT"] and kwpos.upper() != token_p:
                                            f = False
                                    else: 
                                        f = False
                                        
                    if f:
                        if sent in to_add:
                            to_add[sent] += (ind,)
                        else:
                            to_add[sent] = (ind,)
                            
        if to_add:
            result += [tuple([review, to_add])]
                   
                
    return result


# In[285]:


def search(keyword):
    keyword = keyword.strip(' ')
    keywords = keyword.split(' ')
    if len(keywords) == 1:
        result = single_word_search(keyword)
    elif len(keywords) > 1:
        result = collocation_search(keywords)
    elif len(keywords) == 0:
        return 'Пожалуйста, введите запрос'
    return result


# Короче результат функции: список с кортежами. В каждом кортеже 2 элемента: первый — отзыв целиком (с метаинформацией, разбиением по предложениям, изначальным текстом и так далее), второй — словарь. Структура словаря: ```{номер предложения текста: [индекс, с которого начинается первое совпадение (длится ровно столько, сколько слов в запросе), индекс второго совпадения, ... ], предложение: [индекс, индекс] и так далее}```
# то есть если ```[(a1, a2), (b1, b2), (c1, c2)]```
# то предложения вызываются так
# ```
# sents = a2.keys()
# for sent in sents:
#     a1['sentences'][sent]
# ```

# In[ ]:




