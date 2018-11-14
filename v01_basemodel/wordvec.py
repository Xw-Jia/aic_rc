# -*- coding: utf-8 -*-

import gensim
import logging
import jieba
import json
import numpy as np
from tqdm import tqdm
import pickle

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('aic_v1.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s]   >> %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
logger = get_logger()

def seg_line(line):
    sent = list(jieba.cut(line))
    return sent

class MySentences(object):
    def __init__(self, path_list):
       self.path_list = path_list

    def __iter__(self):
        for path in self.path_list:
            logger.info('\nstart process {}'.format(path))
            with open(path, 'r') as f:
                for i, line in tqdm(enumerate(f)):
                    dic = json.loads(line, encoding='utf-8')
                    if len(dic["alternatives"].split("|")) != 3:
                        continue
                    question = dic['query']
                    doc = dic['passage']
                    alternatives = dic['alternatives'].split("|")
                    ans1 = alternatives[0]
                    ans2 = alternatives[1]
                    ans3 = alternatives[2]
                    for sentence in [question, doc, ans1, ans2, ans3]:
                        yield seg_line(sentence)

# model
def train_wordvec(path_list, embed_size=200, data_path=None):
    sentences = MySentences(path_list)
    model = gensim.models.Word2Vec(sentences, size=embed_size, min_count=5, sg=1,
                                   workers=8, hs=0, window=3, iter=5)
    vocabulary = model.wv.vocab   # dict
    words = list(vocabulary.keys())

    function_words = ["PAD", "UNK"]
    words = function_words + words
    logger.info("the vocab size {}".format(len(words)))

    word2id = dict(zip(words, range(len(words))))

    embeddings = np.random.uniform(-0.8, 0.8, (len(words), embed_size))
    embeddings[0] = 0.0
    embeddings[1] = 0.0
    for word, id in word2id.items():
        if word not in vocabulary:
            continue
        embeddings[id] = model[word]

    with open(data_path + "my_word2id.pickle", "wb") as f:
        pickle.dump(word2id, f)

    np.save(data_path+"wordvec_200.npy", embeddings)

if __name__== "__main__":
    # prepare sentence
    data_path = "/home/haixiao.liu/xiepan/project/aic_data/"
    train_path = data_path + "trainingset/train.json"
    valid_path = data_path + "validationset/valid.json"
    testa_path = data_path + "testa/testa.json"
    path_list = [train_path, valid_path, testa_path]

    train_wordvec(path_list, data_path=data_path)

    embeddings = np.load(data_path + "wordvec_200.npy")
    print(embeddings.shape)
    print(embeddings[0])
