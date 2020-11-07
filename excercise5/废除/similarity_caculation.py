#！/usr/bin/env python
#-*-coding:utf-8-*-

import codecs
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim import corpora, models
import numpy as np
import jieba

'''
使用tfidf计算文本之间的相似度
输入：待对齐词条的word_tfidf向量(entry1)，候选集(candidates)（词典，id-词向量）
        entry存储形式：[["称呼", 1.1677906606931854], ["非正式", 0.7915359641643323], ["词义", 0.7672575291416918], ["给予", 0.6087347791379012], ["通俗", 0.6022642083680927], ["大众", 0.5740528857134071],。。。]
输出:在候选集中相似度最大的实体的id，对应相似度的值
计算方法：1、词集合，获取连个词条的word的集合（无重复元素）
        2、词向量，根据词集合得到每个词条的词向量，以tfidf为值，没有的词值为0
        3、计算相似度，根据cos计算两个向量相似度
'''
def txt_similarity_by_tfidf(entry1,candidates):
    #构建词典:key-value:word-index
    word_dictionary={}
    i =0
    for word in entry1:
        if word[0] not in word_dictionary:
            word_dictionary[word[0]]=i
            i+=1
    for id, cand in candidates.items():
        for word in cand:
            if word[0] not in word_dictionary:
                word_dictionary[word[0]] = i
                i += 1
    #构建词向量
    #[0]*len(word_dictionary)构建一个与word_dictionary长度相同并且每个元素为0的list
    word_embedding1=[0]*len(word_dictionary)
    for word in entry1:
        word_embedding1[word_dictionary[word[0]]]=word[1]
    max_sim=0#当前最大相似值
    result=-1
    for id,cand in candidates.items():
        word_embedding2 = [0]*len(word_dictionary)
        for word in cand:
            word_embedding2[word_dictionary[word[0]]] = word[1]
        #计算相似度
        similarity = similarity_by_cos(word_embedding1,word_embedding2)
        if similarity>max_sim:
            max_sim=similarity
            result = id
    #返回对齐实体的id,以及他们之间的文本相似度
    return result,max_sim

#使用cos计算两个向量之间的相似度
def similarity_by_cos(x,y):
    result1 = 0.0
    result2 = 0.0
    result3 = 0.0
    try:
        for i in range(len(x)):
            result1 += x[i] * y[i]  # sum(X*Y)
            result2 += x[i] ** 2  # sum(X*X)
            result3 += y[i] ** 2  # sum(Y*Y)
        result = result1 / ((result2 * result3) ** 0.5)
    except ValueError:
        result=0
    return result



'''
使用LDA计算文本之间的相似度
输入：待对齐词条的words向量(entry1)，候选集(candidates)（词典，id-词向量）
输出:在候选集中相似度最大的实体的id，对应相似度的值
计算方法：
'''
def txt_similarity_by_LDA(entry1,candidates,topic_num):
    # 将待对齐实体与候选集中的词向量合并成文档矩阵
    train = []
    train.append(entry1)
    for cand in candidates.values():
        train.append(cand)
    #构建词频矩阵,训练lda模型
    dictionary = corpora.Dictionary(train)
    corpus = [dictionary.doc2bow(text) for text in train]
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
    #计算相似度
    max_sim=0
    max_id=0
    ent_doc = entry1
    ent_doc_bow = dictionary.doc2bow(ent_doc) #将词向量转化为bow
    ent_doc_lda = lda[ent_doc_bow] #得到文档的主题分布
    list_ent_doc = [i[1] for i in ent_doc_lda] #获取主题分布的概率向量
    for key in candidates:
        cand_doc = candidates[key]
        cand_doc_bow = dictionary.doc2bow(cand_doc) #将词向量转化为bow
        cand_doc_lda = lda[cand_doc_bow] #得到文档的主题分布
        list_cand_doc = [i[1] for i in cand_doc_lda] #获取主题分布的概率向量
        #计算余弦相似度的值
        try:
            sim = np.dot(list_ent_doc, list_cand_doc) / (np.linalg.norm(list_ent_doc) * np.linalg.norm(list_cand_doc))
        except ValueError:
            sim = 0
        if(sim>max_sim):
            max_sim=sim
            max_id=key
    #返回对齐实体的id,以及他们之间的文本相似度
    return max_id,max_sim

'''
使用训练好的LDA模型计算文本之间的相似度
输入：待对齐词条的words向量(entry1)，候选集(candidates)（词典，id-词向量）
输出:在候选集中相似度最大的实体的id，对应相似度的值
计算方法：
'''
def txt_similarity_by_LDA_Model(entry1,candidates,topic_num):
    #获取LDA模型,与字典
    # lda = models.ldamodel.LdaModel.load("../file/"+data_name+'/lda.model')
    # dictionary=corpora.Dictionary.load("../file/"+data_name+"/dict.dict")
    lda = models.ldamodel.LdaModel.load("../file/lda_model/dict_topic_num"+str(topic_num)+"lda.model")
    dictionary = corpora.Dictionary.load("../file/lda_model/dict_topic_num"+str(topic_num)+".dict")
    #计算相似度
    max_sim=0
    max_id=0
    ent_doc = entry1
    ent_doc_bow = dictionary.doc2bow(ent_doc) #将词向量转化为bow
    ent_doc_lda = lda[ent_doc_bow] #得到文档的主题分布
    list_ent_doc = [i[1] for i in ent_doc_lda] #获取主题分布的概率向量
    for key in candidates:
        cand_doc = candidates[key]
        cand_doc_bow = dictionary.doc2bow(cand_doc) #将词向量转化为bow
        cand_doc_lda = lda[cand_doc_bow] #得到文档的主题分布
        list_cand_doc = [i[1] for i in cand_doc_lda] #获取主题分布的概率向量
        #计算余弦相似度的值
        try:
            sim = np.dot(list_ent_doc, list_cand_doc) / (np.linalg.norm(list_ent_doc) * np.linalg.norm(list_cand_doc))
        except ValueError:
            sim = 0
        if(sim>max_sim):
            max_sim=sim
            max_id=key
    #返回对齐实体的id,以及他们之间的文本相似度
    return max_id,max_sim