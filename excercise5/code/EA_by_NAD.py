#！/usr/bin/env python
#-*-coding:utf-8-*-
from excercise5.code.bert_support import BertSupport
from excercise5.code.attributes import entityAttrsSim

def alignment_by_nameAttrBert(xueke,entity_data1,entity_data2,tfidfs_entity1,cand,threshold_for_cands,
                              edit_threshold,bert_threshold,attrWeight,descWeight,count_threshold,
                              resultMap_file, candidates_file,resultDetail_file,entryNumber_file):
    """
    使用索引、属性相似度、文本相似度来做知识融合
    :param xueke: 学科分类
    :param entity_data1: 从数据库中获取的互动百科数据
    :param entity_data2: 百度百科数据
    :param tfidfs_entity1:互动百科的tfidf向量（在文件"../file/xueke/tfidf/hudong_tfidf.json"中
    :param cand: 可以获取候选集的cand对象
    :param threshold_for_cands: 用于计算关键词前缀个数的阈值
    :param edit_threshold: 利用编辑距离计算属性名的相似度的阈值
    :param bert_threshold: 利用bert计算属性名相似度的阈值
    :param attrWeight: 属性相似度的权重
    :param descWeight: 描述信息相似度的权重
    :param count_threshold: 用于判断实体对是否对齐的阈值
    :return:
    """

    print("开始进行实体对齐")

    #将entity_data2中的词条转换为字典，id-entity
    entities2 = {}
    for entry in entity_data2:
        id = entry[0]
        entities2[id] = entry

    # 将entity_data1中的词条使用list装起来
    entities1 = []
    for entry in entity_data1:
        entities1.append(entry)

    resultMapFile = open(resultMap_file,'a',encoding='UTF-8')
    resultDetailFile = open(resultDetail_file,'a',encoding='UTF-8')
    candidatesFile = open(candidates_file,'a',encoding='UTF-8')

    entryNumberFile = open(entryNumber_file,'w+',encoding='UTF-8')
    temp_entry_number = entryNumberFile.readline()
    num = 0
    if(temp_entry_number != ''):
        num = int(temp_entry_number)
    while num<entity_data1.__len__():
        entry1 = entities1[num]
        e_id_1=entry1[0]
        e_name_1 = entry1[1]
        description1 = entry1[3]
        entity_word_tfidf=tfidfs_entity1[str(e_id_1)]

        #用来记录每个候选实体的{id：[attrSim,discSim,AttrSimList]}
        totalSimList = {}
        id_set = set()
        #当存在tfidf词向量时
        if(entity_word_tfidf):
            #获取候选集
            id_set = cand.get_candidate(entry=entry1,word_tfidf=entity_word_tfidf,threshold=threshold_for_cands)
            # candidatesFile.write(str(e_id_1) + " " + str(id_set.__len__()) + " " + str(id_set)+"\n")
            for e_id_2 in id_set:
                entry2 = entities2[int(e_id_2)]
                description2 = entry2[3]

                attrSim,AttrSimList = entityAttrsSim(xueke=xueke,entity1=entry1,entity2=entry2,
                                         edit_threshold=edit_threshold,bert_threshold=bert_threshold)
                descSim = BertSupport().compute_cosine(word1=description1,word2=description2)
                totalSimList[e_id_2] = [attrSim,descSim,AttrSimList]
        resultId = entry1[0] #初始化
        maxSim = 0
        for e_id_2 in totalSimList:
            simList = totalSimList[e_id_2]
            sim = simList[0]*attrWeight+simList[1]*descWeight
            if(sim>maxSim):
                maxSim = sim
                resultId = e_id_2
        if(maxSim>count_threshold):
            resultMapFile.write(str(e_id_1)+" "+str(resultId)+"\n")
            resultDetailFile.write(
                str(e_id_1)+" "+str(e_name_1)+" "+str(maxSim)+" "+
                str(totalSimList[resultId][1])+" "+str(totalSimList[resultId][0])+" "+
                str(totalSimList[resultId][2])+"\n")
        candidatesFile.write(str(e_id_1) + " " + str(id_set.__len__()) + " " + str(id_set) + "\n")
        print("已经对齐" + str(num) + "条数据")
        num += 1
        entryNumberFile.write(num)
        print(entry1)
        print(entities2[int(resultId)])
    print("实体对齐阶段结束！")
