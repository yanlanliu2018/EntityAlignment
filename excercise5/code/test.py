# ！/usr/bin/env python
# -*-coding:utf-8-*-

#异常处理
for i in range(10):
    try:
        10/i
        print(i*10)
    except Exception as e:
        print(i)
        # print(e)
        raise Exception(e)




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