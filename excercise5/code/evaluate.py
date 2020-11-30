#！/usr/bin/env python
#-*-coding:utf-8-*-
from collections import defaultdict
import os

#测试数据集中可对齐实体的个数
# huaxue_entity_count = 193
# jisuanji_entity_count = 181
# renwu_entity_count = 196
# shengwu_entity_count = 187
# yuwenwenxue_entity_count = 192
entity_count = {"huaxue":193,"jisuanji":181,"renwu":196,"shengwu":187,"yuwenwenxue":192}

def get_recallAndAccuracy(xueke,inFile,outFile):
    #存储标准数据的文件  D:\pythonPrograme\entityAlignment\Data Annotations\file\huaxue_hudong_baidu_ids.txt
    # dataFile = "../DataAnnotations/file/"+xueke+"_hudong_baidu_ids.txt"
    dataFile = "D:/pythonPrograme/entityAlignment/DataAnnotations/file/"+xueke+"_hudong_baidu_ids.txt"

    data = open(dataFile,'r',encoding="UTF-8")

    inData = open(inFile,'r',encoding="UTF-8")

    if(not os.path.exists(outFile)):
        os.makedirs(outFile)
    outData = open(outFile+inFile.split("/")[-1],'w',encoding="UTF-8")

    #可对齐实体对个数
    numOf_Reable_Result = entity_count[xueke]

    #记录所有找到的实体对个数
    numOf_Full_Result = 0

    #正确的实体对个数
    numOf_correct_Result = 0

    #将标记数据转换为词典：{hudong_id:baidu_id}
    resultDirect = {}
    for line in data:
        list = line.split(" ")
        resultDirect[list[0]]=int(list[1])

    #统计 正确的实体对个数 与 记录所有找到的实体对个数
    for line in inData:
        list = line.split(" ")
        numOf_Full_Result+=1
        if(int(list[1])==resultDirect[list[0]]):
            numOf_correct_Result += 1

    if(numOf_Full_Result==0):
        numOf_Full_Result=1
    accuracy = numOf_correct_Result/numOf_Full_Result
    recall = numOf_correct_Result/numOf_Reable_Result
    F=0
    if ((accuracy+recall) != 0):
        F = accuracy*recall*2/(accuracy+recall)

    outData.write("accuracy : "+str(accuracy)+" ; recall : "+str(recall)+" ; F : "+str(F))


def get_RR_PC(xueke,inFile):
    #存储标准数据的文件  D:\pythonPrograme\entityAlignment\Data Annotations\file\huaxue_hudong_baidu_ids.txt
    # dataFile = "../DataAnnotations/file/"+xueke+"_hudong_baidu_ids.txt"
    dataFile = "D:/pythonPrograme/entityAlignment/DataAnnotations/file/"+xueke+"_hudong_baidu_ids.txt"

    data = open(dataFile,'r',encoding="UTF-8")

    inData = open(inFile,'r',encoding="UTF-8")

    #可对齐实体对个数
    numOf_Reable_Result = entity_count[xueke]

    #候选实体对个数
    numOf_Full = 0

    #正确的实体对个数
    numOf_correct_Result = 0

    #将标记数据转换为词典：{hudong_id:baidu_id}
    resultDirect = {}
    for line in data:
        list = line.split(" ")
        resultDirect[list[0]]=int(list[1])


    #统计 正确的实体对个数 与 记录所有找到的实体对个数
    for line in inData:
        line = line.replace("{","").replace("'","").replace("\n","").replace("}","").replace(",","")
        list = line.split(" ")
        numOf_Full += int(list[1])
        s = set()
        n = 2
        while n<list.__len__():
            s.add(int(list[n]))
            n+=1
        print(resultDirect[list[0]])
        print(s)
        if(resultDirect[list[0]] in s ):
            numOf_correct_Result+=1

    print("可对其实体对数量："+str(numOf_correct_Result))
    print("候选实体对数量："+str(numOf_Full))



if __name__=='__main__':
    inFile = "../file/huaxue/indexThreshold/candidates/0.53.txt"
    get_RR_PC("huaxue",inFile)
    # num = 7
    # while num< 7.92:
    #     inFile = "../file/yuwenwenxue/edit_threshold/resultMap/"+str('%.2f' % (num/10))+".txt"
    #     outFile = "../file/yuwenwenxue/edit_threshold/recallAndAccuracy/"
    #     get_recallAndAccuracy("yuwenwenxue",inFile,outFile)
    #     num+=1