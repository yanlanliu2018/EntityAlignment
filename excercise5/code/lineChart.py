#！/usr/bin/env python
#-*-coding:utf-8-*-

dir_path = "../file/huaxue/entity_threshold/recallAndAccuracy/"
num = 0
x_data = []
accuracy_data = []
recall_data = []
F_data = []
while num<11:
    file_path = dir_path+str(num/10)
    x_data.append(num)
    try:
        file = open(file_path,'r',encoding="UTF-8")
        line = file.readline().split(" ")
        accuracy_data.append('%.4f' % (float(line[2])))
        recall_data.append('%.4f' % (float(line[6])))
        F_data.append('%.4f' % (float(line[10])))
    except Exception as e:
        print(e)
