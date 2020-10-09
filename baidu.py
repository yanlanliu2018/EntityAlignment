import requests
from lxml import etree
import pymysql
import re
import csv
'''
获取百度百科中5大分类中需要爬取的词条名称
'''
def get_baidu_entity():
    # 需要爬取的分类
    big_fenlei=['renwu','lishi','shehui','jingji','shenghuo']
    base_url="https://baike.baidu.com/"
    big_fenlei_urls=[base_url+x for x in big_fenlei]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    temp=[]
    for url in big_fenlei_urls:
        current_entitys=[]
        response=requests.get(url,headers=headers)
        text=response.content.decode('UTF-8')
        html=etree.HTML(text)
        label1=html.xpath("//div[contains(@class,'g-row')]//li//h4/a/@href")
        if len(label1)>0:
            for i in label1:
                if len(current_entitys)>=200:
                    break
                res= requests.get(i, headers=headers)
                text1=res.content.decode('UTF-8')
                html1 = etree.HTML(text1)
                lis=html1.xpath("//div[contains(@class,'grid-list')]//ul/li")
                if len(lis)>0:
                    for li in lis:
                        entity=li.xpath("./div[@class='list']/a/text()")[0]
                        current_entitys.append(entity)
                    next_url = html1.xpath("//div[@class='page']//a[@id='next']/@href")
                    if len(current_entitys)<200:
                        while(len(next_url)>0):
                            res_url="https://baike.baidu.com/fenlei/"+next_url[0]
                            res2=requests.get(res_url, headers=headers)
                            text2 = res2.content.decode('UTF-8')
                            html2 = etree.HTML(text2)
                            lis2 = html2.xpath("//div[contains(@class,'grid-list')]//ul/li")
                            if len(lis2) > 0:
                                for li in lis2:
                                    if len(current_entitys)>=200:
                                        break
                                    entity = li.xpath("./div[@class='list']/a/text()")[0]
                                    current_entitys.append(entity)
                            if len(current_entitys) >= 200:
                                break
                            next_url = html2.xpath("//div[@class='page']//a[@id='next']/@href")
            temp.append(current_entitys)
    entitys=[]
    for li in temp:
        for entity in li:
            entitys.append(entity)
    # 根据指定的五大分类获取到的1000个百度百科需要爬取的词条，列表每项为词条名
    return entitys
'''
根据获取到的1000个词条名进行爬取信息并插入到百度百科数据库，以及获取互动百科需要爬取的词条名。
'''
def baidu_spider(entitys):
    base_url="https://baike.baidu.com/item/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    dbparams = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'spider',
        'charset': 'utf8',  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = """
        insert into baidu(id,entity_name,attribute,description) values(null,%s,%s,%s)
                        """
    entity_urls=[base_url+entity for entity in entitys]
    extra=[]
    for url in entity_urls:
        s = requests.session()
        s.keep_alive = False
        response = s.get(url, headers=headers)
        text = response.content.decode('UTF-8')
        html = etree.HTML(text)
        # 词条名称
        entry_name = "".join(html.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()"))
        # 词条描述
        discription_list = html.xpath("//div[@class='lemma-summary']/div[@class='para'][1]//text()")
        last_discription=''
        for discription in discription_list:
            if "\n" in discription:
                continue
            discription=discription.replace(" ", "")
            last_discription=last_discription+discription
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
                attribute_name_list_last.append(attribute_name)
        # 属性的值
        dds = html.xpath(
            "//dl[contains(@class,'basicInfo-block')]//dd[contains(@class,'basicInfo-item')]")
        attribute_value_list=[]
        for dd in dds:
            br=dd.xpath("./br")
            values = dd.xpath("./text()")
            attribute_value=''
            if len(br)>0:
                for value in values:
                    value=value.replace("\n", "")
                    attribute_value=value+"，"+attribute_value
            else:
                attribute_value=values[0].replace("\n", "")
            attribute_value_list.append(attribute_value)
        # 将属性名列表和属性值列表生成字典
        attribute = ""
        if len(attribute_name_list_last) == len(attribute_value_list):
            for i in range(len(attribute_name_list_last)):
                if attribute_name_list_last[i].endswith(('名','称')):
                    duoyu_list=re.split('[,，、/]',attribute_value_list[i])
                    for duoyu in duoyu_list:
                        k=[]
                        k.append(duoyu)
                        if k not in extra:
                            extra.append(k)
                attribute += attribute_name_list_last[i] + ":" + attribute_value_list[i] + ";"
        # 插入该词条
        cursor.execute(sql,(entry_name,attribute,last_discription))
        conn.commit()
    # 互动百科需要爬取的词条名
    return extra
'''
互动百科爬取
'''
def hudong_spider(extra):
    base_url = "http://www.baike.com/wiki/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    dbparams = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'spider',
        'charset': 'utf8',  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = """
            insert into hudong(id,entity_name,attribute,description) values(null,%s,%s,%s)
                            """
    entity_urls = [base_url + entity for entity in extra]
    # 词条名相同但是不同实体的词条链接
    tongyi_urls=[]
    for url in entity_urls:
        s = requests.session()
        s.keep_alive = False
        try:
            response = s.get(url, headers=headers,timeout=(2, 1))
            text = response.content.decode('UTF-8')
            html = etree.HTML(text)
            entry_name_list = html.xpath("//div[@class='content-h1']/h1/text()")
            if len(entry_name_list)==0:
                continue
            else:entry_name=entry_name_list[0]
            # 词条描述
            discription = "".join(html.xpath("//div[@id='anchor']/p[1]//text()"))
            tds = html.xpath("//div[@id='datamodule']//div[contains(@class,'module')]//tr/td[not(@class)]")
            # 属性名称和属性值
            attribute = ""
            for td in tds:
                name_list=td.xpath("./strong/text()")
                if len(name_list)>0:
                    attribute_name=name_list[0].replace('：','')
                    attribute_value = "".join(td.xpath("./span/text()"))
                    attribute += attribute_name + ":" + attribute_value + ";"
            ul=html.xpath("//ul[@class='h55']")
            if len(ul)>0:
                lis=ul[0].xpath("./li[not(@class)]")
                for li in lis:
                    tongyi_url=li.xpath("./a/@href")[0]
                    tongyi_urls.append(tongyi_url)
            # # 插入该词条
            cursor.execute(sql, (entry_name,attribute,discription))
            conn.commit()
        except Exception as e:
            print(e)
            continue
    return tongyi_urls

'''
互动百科爬取同名但不同实体的词条
'''
def hudong_more(urls):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    }
    dbparams = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'spider',
        'charset': 'utf8',  # mysql中的编码就是utf8
    }
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = """
                insert into hudong(id,entity_name,attribute,description) values(null,%s,%s,%s)
                                """
    base_url ="http:"
    entity_urls = [base_url+entity for entity in urls]
    for url in entity_urls:
        s = requests.session()
        s.keep_alive = False
        try:
            response = s.get(url, headers=headers)
            text = response.content.decode('UTF-8')
            html = etree.HTML(text)
            entry_name_list = html.xpath("//div[@class='content-h1']/h1/text()")
            if len(entry_name_list)==0:
                continue
            else:entry_name=entry_name_list[0]
            # 词条描述
            discription = "".join(html.xpath("//div[@id='anchor']/p[1]//text()"))
            tds = html.xpath("//div[@id='datamodule']//div[contains(@class,'module')]//tr/td[not(@class)]")
            # 属性名称和属性值
            attribute = ""
            for td in tds:
                name_list=td.xpath("./strong/text()")
                if len(name_list)>0:
                    attribute_name=name_list[0].replace('：','')
                    attribute_value = "".join(td.xpath("./span/text()"))
                    attribute += attribute_name + ":" + attribute_value + ";"
            cursor.execute(sql, (entry_name, attribute, discription))
            conn.commit()
        except Exception as e:
            print(e)
            continue
if __name__ == '__main__':
    entitys=get_baidu_entity()
    extra=baidu_spider(entitys)
    tongyi_urls=hudong_spider(extra)
    hudong_more(tongyi_urls)
