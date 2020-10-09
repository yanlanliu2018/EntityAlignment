#！/usr/bin/env python
#-*-coding:utf-8-*-

from gensim import corpora, models
import numpy as np
import json

'''
利用两个百科知识库的数据作为语料库来训练模型
'''
# 将待对齐实体与候选集中的词向量合并成文档矩阵
def product_LDA_model(topic_num,data_name):
    baidu_words=json.load(open("../file/"+data_name+"/baidu_words.json", encoding='utf-8'))
    hudong_words = json.load(open("../file/"+data_name+"/hudong_words.json", encoding='utf-8'))
    train = []
    for cand in baidu_words.values():
        train.append(cand)
    for cand in hudong_words.values():
        train.append(cand)
    #构建词频矩阵,训练lda模型
    dictionary = corpora.Dictionary(train)
    dictionary.save("../file/"+data_name+'/dict.dict')
    corpus = [dictionary.doc2bow(text) for text in train]
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
    lda.save("../file/"+data_name+'/lda.model')

#合并五个分类中的所有做好分词的json数据
def get_LDA_Model_By_All_Data(topic_num):
    #合并百度数据baidu_words
    baidu_train=[]
    fenlei = ["huaxue","jisuanji","renwu","shengwu","yuwenwenxue"]
    for data_name in fenlei:
        baidu_words=json.load(open("../file/"+data_name+"/baidu_words.json", encoding='utf-8'))
        for cand in baidu_words.values():
            baidu_train.append(cand)

    hudong_train = []
    fenlei = ["huaxue", "jisuanji", "renwu", "shengwu", "yuwenwenxue"]
    for data_name in fenlei:
        hudong_words = json.load(open("../file/" + data_name + "/hudong_words.json", encoding='utf-8'))
        for cand in hudong_words.values():
            hudong_train.append(cand)

    train = baidu_train+hudong_train
    # 构建词频矩阵,训练lda模型
    dictionary = corpora.Dictionary(train)
    dictionary.save("../file/lda_model/dict_topic_num"+str(topic_num)+".dict")
    corpus = [dictionary.doc2bow(text) for text in train]
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
    lda.save("../file/lda_model/dict_topic_num"+str(topic_num)+"lda.model")




if __name__=='__main__':
    for i in range(1,21):
        print("开始构建第"+str(i)+"个模型")
        get_LDA_Model_By_All_Data(i)