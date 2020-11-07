#！/usr/bin/env python
#-*-coding:utf-8-*-
import redis
import pymysql
import json
import re

# 获取百科数据
#从mysql数据库中获取百科数据
def get_data(db,table):
    # **dbparams这种传参格式相当于(host='127.0.0.1',port=3306)这种key=value的方式传入
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
            select * from '''+table
    cursor.execute(sql)
    entry_list=[]
    print('开始获取百科%s数据'%(table))
    i = 0
    for entry in cursor.fetchall():
        i+=1
        entry_list.append(entry)
        if(i%5000==0):print('已经存储了%s条百科词条'%(i))
    conn.close()
    print('数据获取结束')
    return entry_list

# 遍历百科数据，将词条命名以及别名以name-id的形式存入redis
def build_index_nameId(entry_list,db):
    redisDbParams = {
        'host': '127.0.0.1',
        'port': 6379,
        'db': db,
        'encoding': 'utf-8'
    }
    r = redis.Redis(**redisDbParams)
    #清除数据库之前已存在数据
    r.flushdb()
    print('开始制作索引')
    i = 0
    for entry in entry_list:
        i += 1
        if (i % 5000 == 0): print('已经挂载了%s条百科数据' % (i))
        id = entry[0]
        name = entry[1]
        attribute = entry[2]
        # 将词条名的id挂载,使用‘['进行切分，因为在互动百科中词条名有[]备注
        try:
            r.sadd(name.split('（')[0],id)
        except Exception as e :print('id为%s的词条出现问题name:异常信息：%s'%(i,e))
        #将属性中的别名、外文名等与id一起挂载；别名等信息会出现name1、name2、。。的表达形式，要注意
        attributes = attribute.split(';')
        for attr in attributes:
            try:
                list = attr.split(':')
                # 如果属性名以”名“结尾，将其加入索引
                if (len(list)>1 and (list[0].endswith('名') or list[0].endswith('称'))):
                    name_list=re.split('[,，、/（《》）]',list[1])
                    for key_name in name_list:
                        if(key_name==""):continue
                        r.sadd(key_name,id)
            except Exception as e :print('id为%s的词条出现问题attr:异常信息：%s'%(i,e))
    r.save()
    r.close()
    print('索引制作结束')

# 确定挂载词数量；
# 输入：阙值(threshold)，词条的tfidf向量(word_tfidf)；
# 输出：挂载词数量
# 通过cos计算公式来确定挂载数量
def get_keyword_num_byCos(threshold,word_tfidf):
    thre = 0
    for word in word_tfidf:
        thre += word[1] * word[1]
    thre=thre * threshold * threshold
    count = 0
    num = len(word_tfidf)-1
    while num>=0 and count<thre:
        count+=word_tfidf[num][1]*word_tfidf[num][1]
        num-=1
    # if(num<0):num=0
    # else:num+=1
    return num+1

# 根据关键词对百科知识库的词条进行挂载
# 输入：百科库的tfidf数据(data)（baidu_tfidf.json）;字典：id-wordlist
#       redis 数据库号（db）注意：0号与1号已经被使用，这里我们使用2号和3号
# 过程：调用方法确定挂载词数量，根据前缀数量进行挂载
def build_index_keyword_id(data,db,threshold):
    redisDbParams = {
        'host': '127.0.0.1',
        'port': 6379,
        'db': db,
        'encoding': 'utf-8'
    }
    r = redis.Redis(**redisDbParams)
    # 清除数据库之前已存在数据
    r.flushdb()
    print('开始制作索引')
    i = 0
    for id,wordlist in data.items():
        i += 1
        if (i % 5000 == 0): print('已经挂载了%s条百科数据' % (i))
        num=get_keyword_num_byCos(threshold,wordlist)
        # 根据前缀数量，对词条的关键词进行挂载
        for j in range(0,num):
            r.sadd(wordlist[j][0],id)
    r.save()
    r.close()
    print('索引制作结束')

def creatIndex(xueke,nameIndexDB,keywordIndexDB,threshold):
    # 针对百度百科五组词条数据构建索引

    print(xueke)
    print("构建指称索引")
    baidu_entries = get_data('baike_spider', 'baidu_'+xueke)
    build_index_nameId(baidu_entries, nameIndexDB)
    print("构建关键词索引")
    baidu_data = json.load(open('../file/'+xueke+'/tfidf/baidu_tfidf.json', encoding='utf-8'))
    build_index_keyword_id(baidu_data, keywordIndexDB, threshold)
    print("=======================================")
