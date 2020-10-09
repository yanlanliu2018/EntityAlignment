#！/usr/bin/env python
#-*-coding:utf-8-*-
import re
import requests

from selenium import webdriver
import pymysql
from lxml import etree


def craw_for_hudong(filein,fileout,tablename):
    # i = 1
    base_url = 'https://www.baike.com/wiki/'
    for name in open(filein,'r',encoding='utf-8'):
        url = base_url+name.replace('\n','')
        try:
            data = _get_new_data_for_hudong(url=url,fileout=fileout)
            print(data)
            into_mysql(table_name=tablename, data=data)
        except:
            print('craw failed')
        # if(i==1):break
def _get_new_data_for_hudong(url,fileout):
    print('url')
    print(url)
    file = open(fileout,'a',encoding='utf8')
    browser = webdriver.Chrome()
    browser.get(url=url)
    text = browser.page_source
    html = etree.HTML(text)
    try:
        #获取词条名
        entry_name = html.xpath("//div[contains(@class,'bk-title bk-font36 content-title')]/text()")[0].replace(' ', '')
        file.write(entry_name + '\n')
        #获取词条描述信息
        dess = html.xpath("//div[@class='summary']//text()")
        description = "".join(dess).replace(' ', '').replace("\xa0", "")
        #获取词条属性信息
        attrs = html.xpath("//dl[@class='bk-padding-bottom-small bk-padding-top-small']"
                           "|//dl[@class='bk-padding-bottom-small bk-padding-top-small name-large']")
        attributes = ""
        for attr in attrs:
            attr_name = attr.xpath("./dt//text()")
            if(len(attr_name)>0):
                attr_name = attr_name[0].replace('：', '')
                attr_value = "".join(attr.xpath(".//span/text()"))
                attributes = attributes + attr_name + ":" + attr_value + ";"
                if(attr_name.endswith(('名', '称'))):
                    names = re.split('[,，、/]', attr_value)
                    for name in names:
                        file.write(name + '\n')
        attributes = attributes.replace(' ', '').replace("\xa0", "")
        file.close()
        if (len(description) == 0): description = "中文名是" + entry_name
        if (len(attributes) == 0): attribute = "中文名:" + entry_name + ";"
        res_data = {}
        res_data['entry_name'] = entry_name
        res_data['attributes'] = attributes
        res_data['discription'] = description
        return res_data

    except Exception as e:
        print(e)

def craw_for_baidu(filein,tablename):
    # i = 1
    base_url = "https://baike.baidu.com/item/"
    for name in open(filein,'r',encoding='utf-8'):
        url = base_url+name.replace('\n','').replace(' ', '')+'?force=1'
        print('url_to_get_urls')
        print(url)
        try:
            urls = _get_new_urls_for_baidu(url)
            if(len(urls)==0):
                print('url')
                print(url)
                data = _get_new_data_for_baidu(url=url)
                if (data['entry_name'] == ''):
                    continue
                print(data)
                into_mysql(table_name=tablename, data=data)
            else:
                for url in urls:
                    url = 'https://baike.baidu.com'+url
                    print('url')
                    print(url)
                    data = _get_new_data_for_baidu(url=url)
                    if(data['entry_name']==''):
                        continue
                    print(data)
                    into_mysql(table_name=tablename, data=data)
        except:
            print('craw failed')
        # if(i==1):break
#根据百度多义词的页面后某个单词所有的词条url
def _get_new_urls_for_baidu(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    s = requests.session()
    s.keep_alive = False
    response = s.get(url, headers=headers)
    text = response.content.decode('UTF-8')
    html = etree.HTML(text)
    #获取页面中词条的url
    urls = html.xpath(
        "//ul[@class='custom_dot  para-list list-paddingleft-1']/li[@class='list-dot list-dot-paddingleft']/div[@class='para']/a//@href")
    return urls


def _get_new_data_for_baidu(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    s = requests.session()
    s.keep_alive = False
    response = s.get(url, headers=headers)
    text = response.content.decode('UTF-8')
    html = etree.HTML(text)
    # 词条名称
    entry_name = "".join(html.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()"))\
                 +"".join(html.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()"))
    # 词条描述
    discription_list = html.xpath("//div[@class='lemma-summary']/div[@class='para']//text()")
    last_discription = ''
    for discription in discription_list:
        if "\n" in discription:
            continue
        discription = discription.replace(" ", "").replace("\xa0", "")
        last_discription = last_discription + discription
    # 属性的名字列表(属性的名称未作字符串处理)
    attribute_name_list = html.xpath(
        "//dl[contains(@class,'basicInfo-block')]//dt[contains(@class,'basicInfo-item')]/text()")
    attribute_name_list_last = []
    # 对属性的名称作处理
    for attribute_name in attribute_name_list:
        if "\xa0" in attribute_name:
            attribute_name = attribute_name.replace("\xa0", "")
            attribute_name_list_last.append(attribute_name)
        else:
            attribute_name_list_last.append(attribute_name.replace("\xa0", ""))
    # 属性的值
    dds = html.xpath(
        "//dl[contains(@class,'basicInfo-block')]//dd[contains(@class,'basicInfo-item')]")
    attribute_value_list = []
    for dd in dds:
        br = dd.xpath("./br")
        values = dd.xpath(".//text()")
        # print(values)
        attribute_value = ''
        if len(br) > 0:
            for value in values:
                value = value.replace("\n", "").replace("\xa0", "").replace(" ", "")
                attribute_value = value + "，" + attribute_value
        else:
            for value in values:
                attribute_value = attribute_value+'，'+value.replace("\n", "").replace("\xa0", "").replace(" ", "")
        attribute_value_list.append(attribute_value)
    # print(attribute_value_list)
    # 将属性名列表和属性值列表生成字典
    attribute = ""
    if len(attribute_name_list_last) == len(attribute_value_list):
        for i in range(len(attribute_name_list_last)):
            attribute += attribute_name_list_last[i] + ":" + attribute_value_list[i] + ";"

    if (len(last_discription) == 0): last_discription = "中文名是" + entry_name
    if (len(attribute) == 0): attribute = "中文名:" + entry_name + ";"
    res_data = {}
    res_data['entry_name'] = entry_name
    res_data['attributes'] = attribute
    res_data['discription'] = last_discription
    return res_data

def into_mysql(table_name,data):
    if data:
        conn = pymysql.Connect(
            host='127.0.0.1',
            user='root',
            password='123456',
            db='baike_spider',
            port=3306,
            charset='utf8'
        )
        try:
            cursor = conn.cursor()
            sql = 'insert into '+table_name+'(`entity_name`,`attribute`,`description`)values(%s,%s,%s)'
            cursor.execute(sql, (data['entry_name'],data['attributes'],data['discription']))
            conn.commit()
        finally:

            conn.close()

#给获取到的需要到百科中爬去的词条名去重
def name_duplicate(filename):
    file = open(filename, 'r', encoding='utf8')
    names = []
    for line in file:
        line = line.strip()
        if (line in names): continue
        names.append(line)
    file.close()
    file = open(filename, 'w', encoding='utf8')
    for name in names:
        if (len(name) == 0): continue
        file.write(name+'\n')
    file.close()


#获取在第一次爬去过程失败的词汇
def get_failed_word(table_name,filein,fileout):
    #获取数据库中所有词条名
    name_list = []
    conn = pymysql.Connect(
        host='127.0.0.1',
        user='root',
        password='123456',
        db='baike_spider',
        port=3306,
        charset='utf8'
    )
    try:
        cursor = conn.cursor()
        sql = 'select entity_name from ' + table_name
        cursor.execute(sql)
        for name in cursor.fetchall():
            name_list.append(name[0])
    finally:
        conn.close()
    #遍历文本中的名词找到不存在于数据库的词
    file1=open(filein,'r',encoding='utf8')
    file2=open(fileout,'w',encoding='utf8')
    i =0
    print(name_list)
    for line in file1:
        line=line.replace('\n','')
        if(line in name_list):continue
        file2.write(line+'\n')
        i=i+1
    print("爬取失败的词的数量：")
    print(i)



if __name__ == '__main__':

    data = _get_new_data_for_baidu("https://baike.baidu.com/item/李娜")
    print(data)

    # get_failed_word('hudong_jisuanji','file/JiSuanJi_for_hudong.txt','file/Failed_JiSuanJi_for_hudong.txt')

    # #语文文学
    # print("获取互动百科的词条信息——语文")
    # # craw_for_hudong(filein='file/YuWenWenXue_for_hudong.txt',fileout='file/YuWenWenXue_for_baidu.txt',tablename='hudong_yuwenwenxue')
    # print('给词条名单去重')
    # name_duplicate(filename='file/YuWenWenXue_for_baidu.txt')
    # print('获取百度百科的词条信息')
    # craw_for_baidu(filein='file/YuWenWenXue_for_baidu.txt',tablename='baidu_yuwenwenxue')
    #
    # # # 生物
    # print("获取互动百科的词条信息——生物")
    # # craw_for_hudong(filein='file/ShengWu_for_hudong.txt', fileout='file/ShengWu_for_baidu.txt',tablename='hudong_shengwu')
    # print('给词条名单去重')
    # name_duplicate(filename='file/ShengWu_for_baidu.txt')
    # print('获取百度百科的词条信息')
    # craw_for_baidu(filein='file/ShengWu_for_baidu.txt', tablename='baidu_shengwu')
    # #
    # # # 计算机
    # print("获取互动百科的词条信息——计算机")
    # # craw_for_hudong(filein='file/Failed_JiSuanJi_for_hudong.txt', fileout='file/JiSuanJi_for_baidu.txt',tablename='hudong_jisuanji')
    # print('给词条名单去重')
    # name_duplicate(filename='file/JiSuanJi_for_baidu.txt')
    # print('获取百度百科的词条信息')
    # craw_for_baidu(filein='file/JiSuanJi_for_baidu.txt', tablename='baidu_jisuanji')
    # #
    # # 化学
    # print("获取互动百科的词条信息——化学")
    # # craw_for_hudong(filein='file/Failed_JiSuanJi_for_hudong.txt', fileout='file/HuaXue_for_baidu.txt',tablename='hudong_huaxue')
    # print('给词条名单去重')
    # name_duplicate(filename='file/HuaXue_for_baidu.txt')
    # print('获取百度百科的词条信息')
    # craw_for_baidu(filein='file/HuaXue_for_baidu.txt', tablename='baidu_huaxue')
    # #

    # # 人物
    # print("获取互动百科的词条信息——化学")
    # # craw_for_hudong(filein='file/renwu_for_hudong.txt', fileout='file/renwu_for_baidu.txt',tablename='hudong_renwu')
    # print('给词条名单去重')
    # name_duplicate(filename='file/renwu_for_baidu.txt')
    # print('获取百度百科的词条信息')
    # craw_for_baidu(filein='file/renwu_for_baidu.txt', tablename='baidu_renwu')
    # #
