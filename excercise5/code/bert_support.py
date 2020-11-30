# ！/usr/bin/env python
# -*-coding:utf-8-*-
from bert_serving.client import BertClient
import numpy as np

DEV_BERT_SERVER_IP="192.168.1.150"
# DEV_BERT_SERVER_IP="10.166.38.82"
class BertSupport:
    def __init__(self, use_timeout = True):
        if use_timeout:
            # Bert客户端请求BertServer服务，参数ip为服务地址
            self.bc = BertClient(ip =DEV_BERT_SERVER_IP, timeout=15000, check_version=False)
        else:
            self.bc = BertClient(ip=DEV_BERT_SERVER_IP, check_version=False)

    def compute_cosine(self, word1, word2):
        # 使用bert对该对文本进行encode成向量
        if(word1=="" or word2==""):
            return 0
        a = self.bc.encode([word1, word2])
        vector_a = np.mat(a[0])
        vector_b = np.mat(a[1])
        num = float(vector_a * vector_b.T)
        denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
        # 计算向量余弦
        cos = num / denom
        # 计算相似度
        sim = 0.5 + 0.5 * cos
        return sim

    def word_list_vector(self,wordList):
        a = self.bc.encode(wordList)
        d = {}
        for i in range(a.__len__()):
            d[wordList[i]] = np.mat(a[i])
        return d

    def compute_distance(self, word1, word2):
        a = self.bc.encode([word1, word2])
        distance = a[0] - a[1]
        distance_sum = np.sum(distance)
        return np.abs(distance_sum)

    def close(self):
        self.bc.close()

if __name__ == '__main__':
    # 传入两个文本进行相似度计算
    for i in range(50):
        s1='常温常压下，氢气是一种极易燃烧，无色透明、无臭无味且难溶于水的气体。氢气是世界上已知的密度最小的气体，氢气的密度只有空气的1/14，即在0℃时，一个标准大气压下，氢气的密度为0.0899g/L。所以氢气可作为飞艇、氢气球的填充气体（由于氢气具有可燃性，安全性不高，飞艇现多用氦气填充）。氢气是相对分子质量最小的物质，主要用作还原剂。氢气(H2)最早于16世纪初被人工制备，当时使用的方法是将金属置于强酸中。1766–1781年，亨利·卡文迪许发现氢元素，氢气燃烧生成水(2H₂+O₂点燃=2H₂O)，拉瓦锡根据这一性质将该元素命名为“hydrogenium”（“生成水的物质”之意，"hydro"是“水”，"gen"是“生成”，"ium"是元素通用后缀）。19世纪50年代英国医生合信(B.Hobson）编写《博物新编》(1855年）时，把"hydrogen"翻译为“轻气”，意为最轻气体。工业上一般从天然气或水煤气制氢气，而不采用高耗能的电解水的方法。制得的氢气大量用于石化行业的裂化反应和生产氨气。氢气分子可以进入许多金属的晶格中，造成“氢脆”现象，使得氢气的存储罐和管道需要使用特殊材料（如蒙耐尔合金），设计也更加复杂。2018年2月，中国实现氢气的低温制备和存储，荣获科技部2017年度中国科学十大进展。'
        s2='常温常压下，氢气是一种极易燃烧，无色透明、无臭无味且难溶于水的气体。氢气是世界上已知的密度最小的气体，氢气的密度只有空气的1/14，即氢气在1标准大气压和0℃，氢气的密度为0.089g/L。所以氢气可作为飞艇、氢气球的填充气体（由于氢气具有可燃性，安全性不高，飞艇现多用氦气填充）。氢气是相对分子质量最小的物质，主要用作还原剂。氢气(H2)最早于16世纪初被人工制备，当时使用的方法是将金属置于强酸中。1766–1781年，亨利·卡文迪许发现氢元素，氢气燃烧生成水(2H₂+O₂点燃=2H₂O)，拉瓦锡根据这一性质将该元素命名为“hydrogenium”（“生成水的物质”之意，"hydro"是“水”，"gen"是“生成”，"ium"是元素通用后缀）。19世纪50年代英国医生合信(B.Hobson）编写《博物新编》(1855年）时，把"hydrogen"翻译为“轻气”，意为最轻气体。工业上一般从天然气或水煤气制氢气，而不采用高耗能的电解水的方法。制得的氢气大量用于石化行业的裂化反应和生产氨气。氢气分子可以进入许多金属的晶格中，造成“氢脆”现象，使得氢气的存储罐和管道需要使用特殊材料（如蒙耐尔合金），设计也更加复杂。2018年2月，中国实现氢气的低温制备和存储，荣获科技部2017年度中国科学十大进展。'
        print(BertSupport().compute_cosine(s1, s2))
        print(BertSupport().compute_cosine("英文名", "外文名"))
        if i%10==0:
            print("has run %i triples",i)



