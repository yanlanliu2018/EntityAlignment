import requests
from lxml import etree
from  selenium import webdriver

#胡林写的帮我解决互动百科无法爬取有效信息的问题

def a():
    url='https://www.baike.com/wiki/李娜'
    driver_path = r"E:\chromeDriver\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path)
    # 就可以使用driver来操作网页了
    driver.get(url) # 没有返回值
    text=driver.page_source  # 这种方式获取网页内容
    html=etree.HTML(text)
    entry_name=html.xpath("//div[contains(@class,'content-title')]/text()")[0]
    print(entry_name)
if __name__ == '__main__':
    a()