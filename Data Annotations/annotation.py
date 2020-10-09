#！/usr/bin/env python
#-*-coding:utf-8-*-

#从数据库A中获取获取所有词条，遍历
#根据词条a中得到的单词从数据库B中获取词条集合C，将a与C打印到控制台
#从集合C中找到与a匹配的数据，从控制台输入，并将匹配数据的id写入map
#最后将map使用json文件持久化
import re

import pymysql


def _get_hudongId_to_baiduId(hudongtable,baidutable,fileout):
    file = open(fileout,'a',encoding='utf8')
    conn = pymysql.Connect(
        host='127.0.0.1',
        user='root',
        password='123456',
        db='baike_spider',
        port=3306,
        charset='utf8'
    )
    try:
        cursor_baidu = conn.cursor()
        cursor_hudong = conn.cursor()
        sql = "select * from " + hudongtable +" LIMIT 0,561 "
        cursor_hudong.execute(sql)
        for entry in cursor_hudong.fetchall():
            names = set()
            print(entry)
            names.add(entry[1])
            attribute = entry[2]
            attributes = attribute.split(';')
            for attr in attributes:
                try:
                    list = attr.split(':')
                    if (len(list) > 1 and (list[0].endswith('名') or list[0].endswith('称'))):
                        name_list = re.split('[,，、/]', list[1])
                        for name in name_list:
                            names.add(name)
                except Exception as e:
                    print(e)
            print(names)
            for name in names:
                sql = '''select * from ''' + baidutable + ''' where entity_name like \'%''' + name + '''%\''''
                cursor_baidu.execute(sql)
                for i in cursor_baidu.fetchall():
                    print(i)
            print("请选择匹配的id：")
            id = input()
            file.write(str(entry[0]) + ' ' + str(id)+'\n')
            print("================================================")

    finally:
        conn.close()
        file.close()

if __name__=="__main__":
    # _get_hudongId_to_baiduId(hudongtable='hudong_huaxue',baidutable='baidu_huaxue',fileout='file/huaxue_hudong_baidu_ids.txt')

    # _get_hudongId_to_baiduId(hudongtable='hudong_yuwenwenxue', baidutable='baidu_yuwenwenxue',
    #                         fileout='file/yuwenwenxue_hudong_baidu_ids.txt')
    #
    # _get_hudongId_to_baiduId(hudongtable='hudong_shengwu', baidutable='baidu_shengwu',
    #                         fileout='file/shengwu_hudong_baidu_ids.txt')
    #
    _get_hudongId_to_baiduId(hudongtable='hudong_renwu', baidutable='baidu_renwu',
                            fileout='file/renwu_hudong_baidu_ids_1.txt')
    #
    # _get_hudongId_to_baiduId(hudongtable='hudong_jisuanji', baidutable='baidu_jisuanji',
    #                         fileout='file/jisuanji_hudong_baidu_ids.txt')