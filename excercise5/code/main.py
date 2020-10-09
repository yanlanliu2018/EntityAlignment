#！/usr/bin/env python
#-*-coding:utf-8-*-

from excercise5.code import  Index,entities_alignment,tf_idf,LDA


for i in range(1,2):
    # num = i / 10
    # print("阙值为"+str(num))
    # print("开始构建索引")
    # Index.creat(threshold=0.6)
    # print("开始计算相似度")
    entities_alignment.exe_for_5_datas_by_LDA(threshold=0.6, min_sim=0.4, topic_num=4)


