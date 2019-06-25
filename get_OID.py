# -*- coding: utf-8 -*-
import requests
from  lxml import etree
import re
def get_url(url):
    pdf_urls=[]

    '''提取出每个页面的pdf对应的url'''

    response=requests.get(url)
    html = etree.HTML (response.content)
    pdf_url_list=html.xpath('//td/a//@href')
    for pdf_url in pdf_url_list:
        pdf_urls.append('https:'+pdf_url)
    return pdf_urls


def get_OID(url):
    ''
    '''提取每个url的OID'''
    OID_list=[]
    # url='https://www.cisco.com/c/m/zh_cn/about/solutions/enterprise-networks/index.html'
    url_list=get_url(url)
    '''两种不同的url，两种不同的匹配规则'''
    for each in url_list:
        result_one=re.findall(".*en/(.*).html.*",each)
        if result_one:
            OID_list.append(result_one[0])
        result_two=re.findall(".*vertical/(.*).html.*",each)
        if result_two:
            OID_list.append(result_two[0])
    return  OID_list

url = 'https://www.cisco.com/c/m/zh_cn/about/solutions/enterprise-networks/index.html'
for i in get_OID(url):
    print(i)
