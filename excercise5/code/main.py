#！/usr/bin/env python
#-*-coding:utf-8-*-
from excercise5.code import Index, candidate
from excercise5.code.Index import creatIndex
from excercise5.code.tf_idf import exe_for_one_data
from excercise5.code.attributes import attrWeightByFunction
from excercise5.code.EA_by_NAD import alignment_by_nameAttrBert
import os
import json
import time

def EA(parameter):
    # 定义变量
    xueke = "yuwenwenxue"
    nameIndexDB = 9
    keywordIndexDB = 10
    indexThreshold = 0.53  # 计算倒排索引前缀个数的阈值
    edit_threshold = parameter  # 使用编辑距离计算属性名相似度的阈值
    bert_threshold = 0.87  # 使用bert计算属性名相似度的阈值
    attrWeight = 0.5  # 属性相似度权重
    descWeight = 0.5  # 文本相似度权重
    entity_threshold = 0.85  # 实体对相似度阈值
    db = 'baike_spider'  # mysql数据库名称

    #变量的名称和值，用于结果文件的存储
    variable_parameter = "edit_threshold"
    parameter_number = '%.2f' %(edit_threshold)

    # 计算tfidf
    path = "../file/" + xueke + "/tfidf"
    if (not os.path.exists(path)):
        os.mkdir(path)
        exe_for_one_data(xueke)

    # 构建索引 xueke,nameIndexDB,keywordIndexDB,threshold
    # creatIndex(xueke,nameIndexDB,keywordIndexDB,indexThreshold)

    # 计算属性权重(db,entity_table)
    path = "../file/" + xueke + "/weight"
    if (not os.path.exists(path)):
        os.mkdir(path)
        # 计算百度百科知识库的属性值权重
        attrWeightByFunction(db=db, entity_table='baidu_' + xueke)
        # 计算互动百科知识库的属性值权重
        attrWeightByFunction(db=db, entity_table='hudong_' + xueke)

    # 进行实体对齐，
    # 流程：遍历互动百科知识库中实体，
    # 针对每个实体，先获取其候选集，
    # 然后针对候选集合中每个实体，计算属性相似度、文本相似度，
    # 最后，根据相似度的总和进行排序，对top实体进行判定（threshld）
    # (xueke,entity_data1,entity_data2,tfidfs_entity1,cand,threshold_for_cands,
    #                               edit_threshold,bert_threshold,attrWeight,descWeight,count_threshold)

    entity_data1 = Index.get_data(db, 'hudong_' + xueke)
    entity_data2 = Index.get_data(db, 'baidu_' + xueke)
    tfidfs_entity1 = json.load(open('../file/' + xueke + '/tfidf/hudong_tfidf.json', encoding='utf-8'))
    cand = candidate.candidate(name_db=nameIndexDB, key_word_db=keywordIndexDB)

    # 用于存储中间数据的文件
    # 文件“../file/xueke/candidate/参数.text”用于存储候选集合

    path = "../file/" + xueke + "/" + variable_parameter + "/resultMap"
    resultMap_file = "../file/" + xueke + "/" + variable_parameter + "/resultMap/" + str(parameter_number) + ".txt"
    if (not os.path.exists(path)):
        os.makedirs(path)

    candPath = "../file/" + xueke + "/" + variable_parameter + "/candidates"
    candidates_file = "../file/" + xueke + "/" + variable_parameter + "/candidates/" + str(parameter_number) + ".txt"
    if (not os.path.exists(candPath)):
        os.makedirs(candPath)

    detailPath = "../file/" + xueke + "/" + variable_parameter + "/resultDetail"
    resultDetail_file = "../file/" + xueke + "/" + variable_parameter + "/resultDetail/" + str(
        parameter_number) + ".txt"
    if (not os.path.exists(detailPath)):
        os.makedirs(detailPath)

    entryNumberPath = "../file/" + xueke + "/" + variable_parameter + "/temp_entry_number"
    entryNumber_file = "../file/" + xueke + "/" + variable_parameter + "/temp_entry_number/" + str(
        parameter_number) + ".txt"
    if (not os.path.exists(entryNumberPath)):
        os.makedirs(entryNumberPath)

    alignment_by_nameAttrBert(
        xueke=xueke, entity_data1=entity_data1, entity_data2=entity_data2,
        tfidfs_entity1=tfidfs_entity1, cand=cand, threshold_for_cands=indexThreshold,
        edit_threshold=edit_threshold, bert_threshold=bert_threshold,
        attrWeight=attrWeight, descWeight=descWeight, count_threshold=entity_threshold,
        resultMap_file=resultMap_file, candidates_file=candidates_file, resultDetail_file=resultDetail_file,
        entryNumber_file=entryNumber_file)


def fun(num):
    try:
        EA(num / 10)
    except Exception as e:
        print(e)
        fun(num)
        # raise Exception(e)

if __name__=='__main__':
    num = 7.5
    while (num < 7.92):
        print("参数的值为："+str('%.2f' % (num/10)))
        # creatIndex("yuwenwenxue", 9, 10, 0.53)
        fun(num)
        num+=1
        time.sleep(3)
