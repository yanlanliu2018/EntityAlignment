#！/usr/bin/env python
#-*-coding:utf-8-*-
import json
import numpy as np
from excercise5.code import Index
from excercise5.code.bert_support import BertSupport


def Levenshtein_Distance(str1, str2):
    """
    计算字符串 str1 和 str2 的编辑距离
    :param str1
    :param str2
    :return:
    """
    matrix = [[i + j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]

    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if (str1[i - 1] == str2[j - 1]):
                d = 0
            else:
                d = 1

            matrix[i][j] = min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + d)

    return matrix[len(str1)][len(str2)]

def similarityByEdit(str1,str2):
    """
        通过编辑距离计算字符串 str1 和 str2 的相似度
        :param str1
        :param str2
        :return:
        """
    dis = Levenshtein_Distance(str1,str2)
    sim = (1-dis/max(len(str1),len(str2)))*0.9+0.1
    return sim



def  attrWeightByFunction(db,entity_table):
    """
    通过统计计算每个属性的权重

    :param db: 数据库名称
    :param entity_table: 百科数据表
    :return:一个字典，用于存储每个属性名对应的指示函数的值，即属性权重
            fun_attr: {attribute_name:fun(r)}
    """

    entity_data = Index.get_data(db, entity_table)

    #attrs:{attribute_name:{attribute_value:number}}
    attrs = {}
    print('开始统计属性值频率')
    i = 0
    for entry in entity_data:
        i += 1
        if (i % 5000 == 0): print('已经统计了%s条百科数据' % (i))
        attribute = entry[2]
        attributes = attribute.split(';')
        for attr in attributes:
            try:
                list = attr.split(':')
                if(len(list)>1):
                    if(list[0] in attrs):
                        value_number = attrs[list[0]]
                        if(list[1] in value_number):
                            value_number[list[1]]+=1
                        else:
                            value_number[list[1]]=1
                    else:
                        value_number = {}
                        value_number[list[1]]=1
                        attrs[list[0]]=value_number
            except Exception as e:
                print('id为%s的词条出现问题attr:异常信息：%s' % (i, e))

    #fun(r) = HM_value(1/value_number)
    #fun_attr: {attribute_name:fun(r)}
    print('开始计算指示函数')
    fun_attr = {}
    for att_name in attrs:
        name_value_number = attrs[att_name]
        count = 0
        n = len(name_value_number)
        for att_value in name_value_number:
            count+=name_value_number[att_value]
        fun_attr[att_name] = n/count

    filePath = "../file/"+entity_table.split('_')[1]+"/weight/"+entity_table.split('_')[0]+"_attrWeight"
    with open(filePath, 'w', encoding='UTF-8') as f:
        json.dump(fun_attr, f, ensure_ascii=False)

    filePath2 = "../file/" + entity_table.split('_')[1] + "/weight/" + entity_table.split('_')[0] + "_attrs"
    with open(filePath2, 'w', encoding='UTF-8') as f:
        json.dump(attrs, f, ensure_ascii=False)

    return fun_attr

def  attrWeightByFrequence(db,entity_table):
    """
    属性权重=1/属性在实体中出现的次数

    :param db: 数据库名称
    :param entity_table: 百科数据表
    :return:一个字典，用于存储每个属性名对应的指示函数的值，即属性权重
            fun_attr: {attribute_name:fun(r)}
    """

    entity_data = Index.get_data(db, entity_table)

    #attrs:{attribute_name:number}
    attrs = {}
    print('开始统计属性值频率')
    i = 0
    for entry in entity_data:
        i += 1
        if (i % 5000 == 0): print('已经统计了%s条百科数据' % (i))
        attribute = entry[2]
        attributes = attribute.split(';')
        for attr in attributes:
            try:
                list = attr.split(':')
                if(len(list)>1):
                    if(list[0] in attrs):
                        attrs[list[0]] += 1
                    else:
                        attrs[list[0]] = 1
            except Exception as e:
                print('id为%s的词条出现问题attr:异常信息：%s' % (i, e))


    #fun_attr: {attribute_name:1/number}
    print('开始计算指示函数')
    fun_attr = {}
    for att_name in attrs:
        fun_attr[att_name] = 1/attrs[att_name]

    filePath = "../file/"+entity_table.split('_')[1]+"/weight/"+entity_table.split('_')[0]+"_attrWeight"
    with open(filePath, 'w', encoding='UTF-8') as f:
        json.dump(fun_attr, f, ensure_ascii=False)

    filePath2 = "../file/" + entity_table.split('_')[1] + "/weight/" + entity_table.split('_')[0] + "_attrs"
    with open(filePath2, 'w', encoding='UTF-8') as f:
        json.dump(attrs, f, ensure_ascii=False)

    return fun_attr

def entityAttrsSim(xueke,entity1,entity2,edit_threshold,bert_threshold):

    """
    计算实体对之间的属性相似度
    流程：
        遍历entity1的所有属性，找到entity2中与之对应的属性，然后计算属性值的相似度
        最后加上属性权重，计算所有属性的相似度的总和
    :param xueke:学科
    :param entity1:实体1
    :param entity2:实体2
    :param edit_threshold:利用编辑距离计算属性名相似度的阈值
    :param bert_threshold:利用bert计算属性名相似度的阈值
    :return:返回实体对所有属性相似度的和
    """

    #将两个实体的属性转换为key-value的字典
    attribute1 = entity1[2]
    attributes1 = attribute1.split(';')
    attrs1 = {}
    for attr in attributes1:
        attr_list = attr.split(':')
        if (len(attr_list) > 1):
            attrs1[attr_list[0]] = attr_list[1]

    attribute2 = entity2[2]
    attributes2 = attribute2.split(';')
    attrs2 = {}
    for attr in attributes2:
        attr_list = attr.split(':')
        if (len(attr_list) > 1):
            attrs2[attr_list[0]] = attr_list[1]


    #一次性获取所有属性名与属性值的向量表示,并使用字典保存起来，因此就不需要多次调用bert服务,
    #在 str_set 中存储attr中的所有字符串
    str_set = set(attrs1.keys()).union(set(attrs1.values())).union(set(attrs2.keys())).union(set(attrs2.values()))

    #防止sttr_set中含有空字符串
    str_set.add("")
    str_set.remove("")

    str_list = list(str_set)
    attr_string_bert = BertSupport().word_list_vector(wordList=str_list)


    #遍历entity1的所有属性，找到entity2中可以与之对应的属性，并计算属性值的相似度
    #将结果以attrName1:[attrName2,sim]的形式保存在attr_sim_list中
    attr_sim_list = {}
    #AttrSimList [{[attr1Name，attr1'Name]:Sim1,[attr1Value，attr1'Value]:Sim1}......]
    # 记录过程数据用于结果分析
    AttrSimList = []
    attrNameSet2 = set(attrs2.keys())
    for attrName1 in attrs1:
        maxAttrSim = 0
        value1 = attrs1[attrName1]
        attrName2 = ""
        if(attrName1 in attrNameSet2):
            attrName2=attrName1
            maxAttrSim = 1
        else:
            maxName = "temp"
            for name in attrNameSet2:
                tempSim = similarityByEdit(attrName1,name)
                if(tempSim>maxAttrSim):
                    maxAttrSim = tempSim
                    maxName = name
            if(maxAttrSim>edit_threshold):
                attrName2 = maxName
            else:
                maxAttrSim = 0
                maxName = "temp"
                for name in attrNameSet2:
                    if(attrName1!="" and name!=""):
                        vector_a = attr_string_bert[attrName1]
                        vector_b = attr_string_bert[name]
                        num = float(vector_a * vector_b.T)
                        denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
                        # 计算向量余弦
                        cos = num / denom
                        # 计算相似度
                        tempSim = 0.5 + 0.5 * cos
                        if (tempSim>maxAttrSim):
                            maxAttrSim = tempSim
                            maxName = name
                if(maxAttrSim>bert_threshold):
                    attrName2 = maxName
        if(attrName2 !=""):
            attrNameSet2.remove(attrName2)
            # tempSet.remove(attrName2)
            # attrNameSet2 = set(tempSet)
            value2 = attrs2[attrName2]
            if(value1!="" and value2!=""):
                vector_a = attr_string_bert[value1]
                vector_b = attr_string_bert[value2]
                num = float(vector_a * vector_b.T)
                denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
                # 计算向量余弦
                cos = num / denom
                # 计算相似度
                attrSim = 0.5 + 0.5 * cos
                attr_sim_list[attrName1] = [attrName2,attrSim]
                #AttrSimList
                AttrSimList.append([[attrName1,attrName2,maxAttrSim],[value1,value2,attrSim]])

    #
    # #遍历entity1的所有属性，找到entity2中可以与之对应的属性，并计算属性值的相似度
    # #将结果以attrName1:[attrName2,sim]的形式保存在attr_sim_list中
    # attr_sim_list = {}
    # #AttrSimList [{[attr1Name，attr1'Name]:Sim1,[attr1Value，attr1'Value]:Sim1}......]
    # # 记录过程数据用于结果分析
    # AttrSimList = []
    # for attrName1 in attrs1:
    #     maxAttrSim = 0
    #     value1 = attrs1[attrName1]
    #     attrNameSet2 = set(attrs2.keys())
    #     tempSet = set(attrs2.keys())
    #     attrName2 = ""
    #     if(attrName1 in attrNameSet2):
    #         attrName2=attrName1
    #         maxAttrSim = 1
    #     else:
    #         maxName = "temp"
    #         for name in attrNameSet2:
    #             tempSim = similarityByEdit(attrName1,name)
    #             if(tempSim>maxAttrSim):
    #                 maxAttrSim = tempSim
    #                 maxName = name
    #         if(maxAttrSim>edit_threshold):
    #             attrName2 = maxName
    #         else:
    #             maxAttrSim = 0
    #             maxName = "temp"
    #             for name in attrNameSet2:
    #                 tempSim = BertSupport().compute_cosine(attrName1, name)
    #                 if (tempSim>bert_threshold):
    #                     maxAttrSim = tempSim
    #                     maxName = name
    #             if(maxAttrSim>bert_threshold):
    #                 attrName2 = maxName
    #     if(attrName2 !=""):
    #         tempSet.remove(attrName2)
    #         attrNameSet2 = set(tempSet)
    #         value2 = attrs2[attrName2]
    #         attrSim = BertSupport().compute_cosine(value1, value2)
    #         attr_sim_list[attrName1] = [attrName2,attrSim]
    #
    #         #AttrSimList
    #         AttrSimList.append([[attrName1,attrName2,maxAttrSim],[value1,value2,attrSim]])

    #加上属性的权重值计算属性的总相似度
    filePath1 = "../file/" + xueke + "/weight/hudong_attrWeight"
    filePath2 = "../file/" + xueke + "/weight/baidu_attrWeight"
    hudong_attrWeight = json.load(open(filePath1, encoding='utf-8'))
    baidu_attrWeight = json.load(open(filePath2, encoding='utf-8'))

    countSim = 0
    for attrName1 in attr_sim_list:
        attrName2 = attr_sim_list[attrName1][0]
        attrSim = attr_sim_list[attrName1][1]
        # countSim += attrSim*(baidu_attrWeight[attrName2]+hudong_attrWeight[attrName1])/2
        countSim += attrSim
    if(attr_sim_list.__len__()>0):
        countSim = countSim/attr_sim_list.__len__()

    return countSim,AttrSimList


