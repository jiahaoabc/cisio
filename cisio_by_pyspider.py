#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-21 14:50:03
# Project: cisio_spider

from pyspider.libs.base_handler import *
import re
import pymongo
import os
import requests
from lxml import etree


class Handler (BaseHandler):
    #  post_url='https://s177775138.t.eloqua.com/e/f2'
    #  session = requests.Session()
    # headers={
    #        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    #         'Host': 's177775138.t.eloqua.com',
    #        'Origin': 'https://www.cisco.com',
    #    }

    crawl_config = {

        #     "post_url"=post_url#      "session"=session#    "headers"= headers
    }
    @every (minutes=24 * 60)
    def on_start(self):
        self.crawl ('https://www.cisco.com/c/m/zh_cn/about/solutions/enterprise-networks/index.html',
                    callback=self.index_page, validate_cert=False)

    @config (age=10 * 24 * 60 * 60)
    def index_page(self, response):
        # ����ҳ������url����ȡÿ��url��Ӧ��oidֵ�����ظ�login����
        for each in response.doc ('td > a').items ():
            result_one = re.findall (".*en/(.*).html.*", each.attr.href)
            result_two = re.findall (".*vertical/(.*).html.*", each.attr.href)
            if (result_one):
                self.crawl (each.attr.href, callback=self.login, save={'a': result_one}, validate_cert=False)
                oid = result_one
            elif (result_two):
                self.crawl (each.attr.href, callback=self.login, save={'a': result_two}, validate_cert=False)
                oid = result_two

    @config (priority=2)
    def detail_page(self, response):
        # ����ÿ��pdf��Ӧ�ı��⡢��С����url����mongodb����pdf�ļ��������ݿ�
        i = response.save[ 'i' ]
   #     url = response.url
        title = response.doc ('.asset-desc').text ()
        size = response.doc ('.asset-info').text ()
        pdf_url = response.doc ('.download-button').attr.href
        print(pdf_url)
        content = requests.get (pdf_url).content
        item = {}
        item[ "pdf_title" ] = title
        item[ "pdf_size" ] = size
        item[ "pdf_url" ] = pdf_url
       # pdf_file_path = os.path.abspath ('') + str (i) + '.pdf'
        pdf_file_path = 'E:\cisio_demo\cisio_pdf\%s.pdf'%title
        print(pdf_file_path)
        with open (pdf_file_path, 'wb') as f:
            f.write (content)
        print(item)
        client = pymongo.MongoClient (host='localhost', port=27017)
        db = client.test
        collection = db.cisco_pyspider
        collection.insert (item)
        #  collection.insert(data)

    #    '.download-button'

    def login(self, response):
        # postע���¼����¼���ҳ�淵�ظ�detail_page����
        url = response.url
        Oid = response.save[ 'a' ]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
            'Host': 's177775138.t.eloqua.com', 'Origin': 'https://www.cisco.com', }
        post_data = {
            'elqFormName': 'GRSDynamicOfferForm',
            'elqSiteId': '177775138',
            'elqCampaignId': '',
            'lastName': '******',
            'emailAddress': '********com',
            'busPhone': '******',
            'company': '*****',
            'dropdownMenu': '******',
            'jobLevel1': 'CXO/Executive', 
            'department': 'MIS/IT - Applications Dev',
            'dropdownMenu2': 'Chemical & Petroleum', 
            'opt_in': 'on', 
            'updatedby': 'Form - submit',
            'emailName': '',
            'FORMID': '3473',
            'hiddenField3': '',
            'hiddenField5': '177775138', 
            'CCID': 'cc000069',
            'DTID': 'odicdc000510',
            'OID': Oid, 
            'ECID': '3495',
            'keycode1': '',
            'GCLID': '', 'keywords': '',
            'campaign': '', 'countrySite': '', 'creative': '', 'position': '', 'placement': '', 'referingSite': '',
            'search': '', 'hiddenField': '', 'hiddenField2': 'CHINA', 'offerName': '', 'offerSize': '', 'offerURL': '',
            'offerURL1': ''}
        self.crawl ('https://s177775138.t.eloqua.com/e/f2', callback=self.detail_page, save={'i': Oid}, method='POST',
                    data=post_data, headers=headers, validate_cert=False)