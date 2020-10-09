#！/usr/bin/env python
#-*-coding:utf-8-*-

"""
用来清洗数据中杂质
1、互动百科属性数据
1.1
互动百科每条数据的属性中存在“创建者、浏览次数、编辑次数、最近更新”四个无用属性，对其进行去除。
方式：获取数据库中属性数据的列表，去掉最后四条属性，再重新写入数据库
注意：有词条去掉无用属性后，属性数量可能为0，我们将词条名作为一条属性进行输入。
1.2
属性名中存在“\Xao”的杂质
使用字符串的replace方法替换掉
2、去掉百度百科中的词条信息中的所有空格


"""
import pymysql


def hudong(db,table):
    mysqlDbparams = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': db,
        'charset': 'utf8'  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**mysqlDbparams)
    cursor = conn.cursor()
    sql = '''
                select * from ''' + table
    cursor.execute(sql)
    entry_list = []
    print('开始获取百科%s数据' % (table))
    for entry in cursor.fetchall():
        entry_list.append(entry)
    print('数据获取结束')

    n=1
    for entry in entry_list:
        print("词条的数量：")
        print(n)
        n=n+1
        id = entry[0]
        name = entry[1]
        attr = entry[2]
        attr_list = attr.split(';')
        attr = ""
        for i in range(len(attr_list)-5):
            attr = attr + attr_list[i].replace("\xa0","").replace("\Xa0","")+";"
        if(attr==""):
            attr = "中文名:"+name+";"
        sql = '''
                UPDATE %s SET  attribute=%s where id=%s'''% (table,'"'+attr+'"',id)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

def baidu(db,table):
    mysqlDbparams = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': db,
        'charset': 'utf8'  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**mysqlDbparams)
    cursor = conn.cursor()
    sql = '''
                select * from ''' + table
    cursor.execute(sql)
    entry_list = []
    print('开始获取百科%s数据' % (table))
    for entry in cursor.fetchall():
        entry_list.append(entry)
    print('数据获取结束')

    n=1
    for entry in entry_list:
        print("词条的数量：")
        print(n)
        n=n+1
        id = entry[0]
        name = entry[1]
        attr = entry[2]
        des = entry[3]

        attr = attr.replace("\xa0","").replace("\Xa0","").replace(" ","")
        des = des.replace("\xa0", "").replace("\Xa0", "").replace(" ", "")
        try:
            sql = '''
                    UPDATE %s SET  attribute=%s,description=%s where id=%s'''% (table,'"'+attr+'"',"'"+des+"'",id)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print("修改失败")
            print(entry)
            print(e)
            continue



if __name__ == '__main__':
    baidu("baike_spider", "hudong_huaxue_1")
    # hudong("baike_spider", "hudong_huaxue")
    # hudong("baike_spider", "hudong_jisuanji")
    # hudong("baike_spider", "hudong_renwu")
    # hudong("baike_spider", "hudong_shengwu")
    # hudong("baike_spider", "hudong_yuwenwenxue")

    # baidu("baike_spider", "baidu_huaxue")
    # baidu("baike_spider", "baidu_jisuanji")
    # baidu("baike_spider", "baidu_renwu")
    # baidu("baike_spider", "baidu_shengwu")
    # baidu("baike_spider", "baidu_yuwenwenxue")