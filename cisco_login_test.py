#coding: utf-8 requests
import requests
from lxml import etree
import re
import os
from mongo_test import MongoOperator
class Login(object):
    def __init__(self):
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
            'Host': 's177775138.t.eloqua.com',
            'Origin': 'https://www.cisco.com',

        }
        self.post_url='https://s177775138.t.eloqua.com/e/f2'
        self.session=requests.Session()

    def login(self,name,email,phone,com,addr,OID):
        post_data={
            'elqFormName': 'GRSDynamicOfferForm',
            'elqSiteId': '177775138',
            'elqCampaignId': '',
            'lastName': name,
            'emailAddress': email,
            'busPhone': phone,
            'company': com,
            'dropdownMenu': addr,
            'jobLevel1': 'Employee',
            'department': 'MIS / IT - Storage',
            'dropdownMenu2': 'Healthcare',
            'opt_in': 'on',
            'updatedby': 'Form - submit',
            'emailName':'',
            'FORMID': '3473',
            'hiddenField3':'',
            'hiddenField5': '177775138',
            'CCID': 'cc000069',
            'DTID': 'odicdc000510',
            'OID': OID,
            'ECID': '3495',
            'keycode1':'',
            'GCLID':'',
            'keywords':'',
            'campaign':'',
            'countrySite':'',
            'creative':'',
            'position':'',
            'placement':'',
            'referingSite':'',
            'search':'',
            'hiddenField':'',
            'hiddenField2': 'CHINA',
            'offerName':'',
            'offerSize':'',
            'offerURL':'',
            'offerURL1':''
        }
        response=self.session.post(self.post_url,data=post_data,headers=self.headers)
        if response.status_code==200:
            return self.dynamics(response.content)


    def dynamics(self,html):
        ''
        '''解析每个pdf的标题，大小，url'''
        selector=etree.HTML(html)
        pdf_url=selector.xpath('/html/body/div[1]/div[2]/a//@href')[0]
        title=selector.xpath('/html/body/div[1]/div[2]/div/div[1]/text()')[0]
        size=selector.xpath('/html/body/div[1]/div[2]/div/div[2]/text()')[0]

        return title,size,pdf_url

    def get_Url(self,url):
        pdf_urls = [ ]

        '''提取出每个页面的pdf对应的url'''

        response = requests.get(url)
        html = etree.HTML (response.content)
        pdf_url_list = html.xpath ('//td/a//@href')
        for pdf_url in pdf_url_list:
            pdf_urls.append ('https:' + pdf_url)
        return pdf_urls

    def get_OID(self,url):
        ''
        '''提取每个url的OID'''
        OID_list = [ ]
        # url='https://www.cisco.com/c/m/zh_cn/about/solutions/enterprise-networks/index.html'
        url_list =self.get_Url (url)
        '''两种不同的url，两种不同的匹配规则'''
        for each in url_list:
            result_one = re.findall (".*en/(.*).html.*", each)
            if result_one:
                OID_list.append (result_one[ 0 ])
            result_two = re.findall (".*vertical/(.*).html.*", each)
            if result_two:
                OID_list.append (result_two[ 0 ])
        print len(OID_list)
        return OID_list

if __name__=="__main__":
    ''''下载pdf文件、存入相关字段到mongodb'''
    db = MongoOperator ('127.0.0.1', 27017, 'test', 'cisco_collection')
    login = Login ()
    url = 'https://www.cisco.com/c/m/zh_cn/about/solutions/enterprise-networks/index.html'
    OID_list=login.get_OID(url)
    for i,oid in enumerate(OID_list):
        title, size, pdf_url =login.login (name='jiahao', email='1130056563@qq.com', phone='18271137390', com='abc', addr='北京',OID=oid)
        print(title,size,pdf_url)
        item={}
        item["pdf_title"]=title
        item["pdf_size"]=size
        item["pdf_filename"]=i
        item["pdf_url"]=pdf_url
        db.insert(item)
        pdf_file_path = os.path.abspath ('')  + str (i) + '.pdf'
        r=requests.get(pdf_url)
        with open(pdf_file_path,'wb') as f:
            f.write(r.content)





