#！/usr/bin/env python
#-*-coding:utf-8-*-
import re

list = ['化学式', 'H₂']
if (len(list) > 1 and (list[0].endswith('名') or list[0].endswith('称'))):
    name_list = re.split('[,，、/]', list[1])
# 行路难（玄觞 / 汐音社演唱歌曲）
# name = [1,2,3,4]
# for i in name:
#     print(i)
#     print("请选择匹配的id：")
#     id = input()
#     print(id)
#     print("=========================")