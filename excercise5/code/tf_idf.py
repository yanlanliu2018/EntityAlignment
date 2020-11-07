#！/usr/bin/env python
#-*-coding:utf-8-*-
import json
from collections import defaultdict
import pymysql
import jieba
import math

#将停用词文档转换为list
def stopwordslist(file):
    stopwords = [line.strip() for line in open(file, encoding='UTF-8').readlines()]
    stopwords.append(' ')
    return stopwords

'''
从mysql数据库中获取数据（所有文本数据）并对其进行，分词、去除停用词等处理工作
'''
def get_data(db,table):
    # **dbparams这种传参格式相当于(host='127.0.0.1',port=3306)这种key=value的方式传入
    mysqlDbparams = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': db,
        'charset': 'utf8'  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**mysqlDbparams)
    cursor = conn.cursor()
    sql='select * from %s'%(table) # limit 0,50
    cursor.execute(sql)
    entry_list={}
    print('开始获取百科数据')
    i = 0
    # 我们对所有文本进行分词、去除停用词，并以list的形式存，
    #处理后，entry的数据形式：{key:id-value:wordlist}
    stop_word_lit = stopwordslist("../file/StopWord.txt")
    for entry in cursor.fetchall():
        i+=1
        id = entry[0]
        # 使用搜索引擎模式进行分词，获取list
        # print("词条的id：%s"%(id))
        word_list=[]#所有文本构成的分词列表
        for index in range(1,len(entry)):#遍历字段
            if(entry[index]):
                des_list = jieba.lcut(entry[index])
                resultList = []#字段构成的分词列表
                #去除停用词
                for word in des_list:
                    if(word not in stop_word_lit):
                        # des_list.remove(word)
                        resultList.append(word)
                word_list+=resultList
        entry_list[id]=word_list
        if(i%5000==0):print('已经对%s条%s的百科词条进行了预处理'%(i,db))
    conn.close()

    print('数据获取结束')
    return entry_list

# 输入：做好预处理的两个百科数据库
# 输出：计算好tfidf值的data数据集合
def tf_idf(datas):
    #存储所有词的idf
    word_idf=defaultdict(int)
    i = 0
    for data in datas:
        i=i+1
        print("开始对%s号数据库的每个实体进行词频统计"%(i))
        #统计前，entry的数据形式：{id:[description word list]}
        num = 0
        for id,wordlist in data.items():
            num+=1
            if(num%5000==0):print("已经统计了%s个词条的词频"%(num))
            #统计词频
            # 使用defaultdict(int)构建词典，在取值时，如果词典没有该key，不会报错，会返回int对应的默认值
            doc_frequency = defaultdict(int)
            sumword = len(wordlist)
            for word in wordlist:
                doc_frequency[word] += 1
            for word in doc_frequency.keys():
                #计算tf值
                doc_frequency[word] = doc_frequency[word]/sumword
                #统计每个词在多少个词条中出现过
                word_idf[word]+=1
            #统计词频后，entry的数据形式{id,{word1：tf1，word2：tf2.。。。}}
            data[id]=doc_frequency
    print("词频统计结束！")
    print("开始计算每个词的idf")
    #计算每个词的idf
    doc_num=len(datas[0])+len(datas[1])
    for word in word_idf:
        word_idf[word] = math.log(doc_num/(word_idf[word]+1))*100
    print("idf计算结束！")
    #计算每个词条中词的tfidf
    i=0
    for data in datas:
        i = i + 1
        print("开始对%s号数据库的每个实体进行tfidf计算" % (i))
        num = 0
        for id, wordlist in data.items():
            num += 1
            if (num % 5000 == 0): print("已经计算了%s个词条的tfidf" % (num))
            # 统计前，entry的数据形式{id,{word1：tf1，word2：tf2.。。。}}
            # 统计后，entry的数据形式{id,{word1：tfidf1，word2：tfidf2.。。。}}
            for word in wordlist:
                wordlist[word] = wordlist[word]*word_idf[word]
            #对word_dic按照tfidf的值进行排序，
            # 排序后，entry的数据形式{id:[word1：tfidf1，word2：tfidf2.。。。]}
            data[id] = sorted(wordlist.items(), key=lambda kv: (kv[1], kv[0]),reverse=True)
    print("tfidf计算结束！")
    #data的数据形式：{id:[(word1,tfidf1)，(word2,tfidf2).。。。]],....}
    return datas[0],datas[1],word_idf

#使用json文件将data数据进行持久化
#方便后期的使用
def data2txt(data,file):
    with open(file, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False)

def main(database,baidu_table,hudong_table,file_for_WordIdfs,file_for_hudong_tfidf,file_for_baidu_tfidf,file_for_baidu_words,file_for_hudong_words):
    print("开始对词条计算tfidf数据")
    baidudata = get_data(database, baidu_table)
    hudongdata = get_data(database, hudong_table)
    data2txt(baidudata,file_for_baidu_words)
    data2txt(hudongdata,file_for_hudong_words)
    datas = [baidudata, hudongdata]
    baidu, hudong, idfs = tf_idf(datas)
    data2txt(baidu, file_for_baidu_tfidf)
    data2txt(hudong,file_for_hudong_tfidf)
    data2txt(idfs, file_for_WordIdfs)

def exe_for_one_data(xueke):
    print("开始对"+xueke+"类词条计算")
    baidudata = get_data("baike_spider", "baidu_"+xueke)
    hudongdata = get_data("baike_spider", "hudong_"+xueke)
    data2txt(baidudata, "../file/"+xueke+"/tfidf/baidu_words.json")
    data2txt(hudongdata, "../file/"+xueke+"/tfidf/hudong_words.json")
    datas = [baidudata, hudongdata]
    baidu, hudong, idfs = tf_idf(datas)
    data2txt(baidu, "../file/"+xueke+"/tfidf/baidu_tfidf.json")
    data2txt(hudong, "../file/"+xueke+"/tfidf/hudong_tfidf.json")
    data2txt(idfs, "../file/"+xueke+"/tfidf/WordIdfs.json")
