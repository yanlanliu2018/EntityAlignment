# ！/usr/bin/env python
# -*-coding:utf-8-*-

from excercise5.code.bert_support import BertSupport

#将字典里的所有key与value作为字符串存在set里
direction1 = {"a":"1","b":"2","c":"3"}
direction2 = {"b":"4","e":"5","f":"2"}
s = set(direction1.keys()).union(set(direction1.values())).union(set(direction2.keys())).union(set(direction2.values()))
s.add("")
s.remove("")
# s = set(direction2.keys()).union(s)
# s = set(direction1.values()).union(s)
# s = set(direction2.values()).union(s)
print(s)
l = list(s)
print(l)
vect = BertSupport().word_list_vector(wordList=l)
print(vect)


# #
# inFile = "../file/huaxue/entity_threshold/resultMap/0.95.txt"
# print(inFile.split("/")[-1])

#定义全局变量
# huaxue_entity_count = 193
# jisuanji_entity_count = 181
# renwu_entity_count = 196
# shengwu_entity_count = 187
# yuwenwenxue_entity_count = 192
#
# def function():
#     print(huaxue_entity_count)
#     print(jisuanji_entity_count)
#
# function()


#异常处理
# for i in range(10):
#     try:
#         10/i
#         print(i*10)
#     except Exception as e:
#         print(i)
#         # print(e)
#         raise Exception(e)




# def func(i):
#     if (i == 1):
#         return i
#     else:
#         return i*10
#
# for item in range(10):
#     print(func(item))


# entryNumber_file="../file/huaxue/entity_threshold/temp_entry_number/0.95.txt"
#
# entryNumberFile = open(entryNumber_file,'r',encoding='UTF-8')
# temp_entry_number = entryNumberFile.readline()
# num = 0
# print(temp_entry_number)
# if(temp_entry_number != ''):
#     num = int(temp_entry_number)
# print(num)
# num+=2
# entryNumberFile = open(entryNumber_file, 'w', encoding='UTF-8')
# entryNumberFile.write(str(num))