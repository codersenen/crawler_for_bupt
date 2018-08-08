#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd     # 对数据进行读写及计算统计模块
import requests          #处理URL资源
from bs4 import BeautifulSoup
from idna import unicode
import re
import xlwt
import pymysql

url = 'https://bbs.byr.cn/user/ajax_login.json'   # 点击登录之后的跳转网址
my_header = {'x-requested-with':'XMLHttpRequest'}
byr_data = {'id':'sunday7','passwd':'LY5237YL'}

s = requests.Session()   #二次请求会话
r = s.post(url,data = byr_data,headers = my_header)   #网站登录
# print (r.text)
def getHtml(page):
    for index in range(page):      #爬取多页内容
        hot_url='https://bbs.byr.cn/board/ParttimeJob?p='+str(index)+'&_uid=sunday7'
        hot = s.get(hot_url,headers = my_header)
        html2=hot.content
        if index==0:
            html=html2
        else:
            html=html+html2
    return html

def parse(html):
    lj=BeautifulSoup(html,'html.parser') #使用美丽汤进行解析html的标签内容
    job=lj.find_all('td','title_9')      #寻找目标所在的标签
    colt=[]
    for rec in job:
        totalJob=rec.a.string
        colt.append(totalJob)


    job=lj.find_all('td','title_9')
    colt=[]
    webColt=[]
    for rec in job:
        totalJob=rec.a.string
        totalWeb=rec.a.attrs['href']
        colt.append(totalJob)
        webColt.append('https://bbs.byr.cn'+totalWeb)


    T=lj.find_all('td','title_10')
    if T:
        Tcolt=[]
        p=0
        for rec in T:
            if p%2==0:
                totalDate=rec.string
                Tcolt.append(totalDate)
            p=p+1
    else:
        print("这里有异常啊")


    return Tcolt,colt,webColt


chtml=getHtml(5)
inf1,inf2,inf3 = parse(chtml)

#print(inf1)
#print(inf2)
#print(inf3)

f = xlwt.Workbook() #创建工作簿
sheet1 = f.add_sheet(u'jobs',cell_overwrite_ok=True) #创建sheet
row0 = ["发布时间","岗位信息","链接"]

for i in range(len(row0)):
    sheet1.write(0,i,row0[i])#表格的第一行开始写。第一列，第二列。。。。
#sheet1.write(0,0,start_date,set_style('Times New Roman',220,True))
for i in range(len(inf1)):
    sheet1.write(i+1,0,inf1[i])
for i in range(len(inf2)):
    sheet1.write(i+1,1,inf2[i])
for i in range(len(inf3)):
    sheet1.write(i+1,2,inf3[i])

f.save('D:/Pythonwork/joblist.xls')

db = pymysql.connect(host='localhost', user='root',password= '151886',port = 3306)
cursor = db.cursor()
cursor.execute('SELECT VERSION()')
data = cursor.fetchone()
print('Database version:', data)
cursor.execute("CREATE DATABASE getjobs DEFAULT CHARACTER SET utf8 ")

db = pymysql.connect(host='localhost', user='root',password= '151886',port = 3306,db = 'getjobs')
cursor = db.cursor()
sql = 'CREATE TABLE TF NOT EXISTS jobs (time VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, links VARCHAR (255) NOT NULL, PRIMARY KEY (links)）'
cursor.execute(sql)
sql = 'INSERT INTO jobs(time, name, links) Values (%s, %s, %s)'
for i in range(len(inf1)):
    try:
        cursor.execute(sql,(inf1[i], inf2[i], inf3[i]))
        db.commit()
    except:
        db.rollback()
db.close()
