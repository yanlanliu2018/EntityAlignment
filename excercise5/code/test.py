# ！/usr/bin/env python
# -*-coding:utf-8-*-
candidatesFile = open("../file/candidates.txt",'w')
e_id_1 = 1
id_set = {1,2,3,4}
candidatesFile.write(str(e_id_1)+" "+str(id_set.__len__())+" "+str(id_set))

candidatesFile = open("../file/candidates.txt",'r')
line = candidatesFile.readline()
list = line.split(" ")
e_id_1 = int(list[0])
id_set = int(list[1])
print(e_id_1.__class__)
print(e_id_1)
print(id_set.__class__)
print(id_set)
