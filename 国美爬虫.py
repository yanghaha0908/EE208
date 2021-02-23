# SJTU EE208
import os
import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
import socket
import threading
import queue
import time
import random

from urllib import error
from bs4 import BeautifulSoup

dic={}
pro_list=[]
f = open('ip.txt','r')#ip代理文件
for line in f.readlines():
    ipd = {}
    ipd["http"]=line
    pro_list.append(ipd)
f.close()
#使用代理ip，随机在池子中选


def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def is_digit(n):
    return n in "0123456789."

def ch(m):

    a=filter(is_digit, list(m)) 
    a=''.join(list(a))
    return a

def get_page(page):    

    try:
        proxy_handler = urllib.request.ProxyHandler(random.choice(pro_list))
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

        content = urllib.request.urlopen(page,timeout=10).read().decode('utf-8',"ignore")
        soup=BeautifulSoup(content,features="html.parser")


        folder = 'html'  # 存放网页的文件夹
        filename = valid_filename(page)  # 将网址变成合法的文件名
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        f = open(os.path.join(folder, filename), 'w',encoding='utf-8')
        f.write(content)  # 将网页存入文件
        f.close()

        #提取各项信息------------------------------------------------------------

        a=page.split('/')
        a1=a[-1].split('-')
        can1=a1[0]
        can2=a1[1].split('.')[0]
        #print(can1,can2)

        s=str(soup)
        p1=s.find("shopNo:")
        shop=ch(s[p1:p1+22])
        #print(shop)
        #requesturl="https://ss.gome.com.cn/item/v1/d/m/store/unite/G001/fshop/"+can1+"/"+can2+"/11010000/N/11010200/110102002/null/1/flag/item/"
        requesturl="https://ss.gome.com.cn/item/v1/d/m/store/unite/"+shop+"/pop/"+can1+"/"+can2+"/11010000/N/11010200/110102002/null/1/flag/item/"
        #print(requesturl)

        for i in soup.findAll('div',{'class' :'hgroup'}):  
            name=i.contents[1].string   #商品名称

        for i in soup.findAll('div',{'class' :'jqzoom'}):  
            imgurl=i.contents[1].get('jqimg','')   #商品图片地址

        content1 = urllib.request.urlopen(requesturl,timeout=10).read().decode('utf-8',"ignore")
        soup1=BeautifulSoup(content1,features="html.parser")

        request=str(soup1)
        #print(request)

        ps=request.find("salePrice")
        pe=request.find(",",ps)
        price=request[ps+11:pe] #str   价格
        if price=='':
            price="NULL"
        #print("jiage",price)

        ps=request.find("commentsOld")
        pe=request.find("}",ps)

        if ps==-1:
            ps=request.find("comments")
            pe=request.find(",",ps)

        #print(ps,pe)    
        comment=request[ps+8:pe]  #str   评论总数
        comment=ch(comment)
        #print(comment)

        ps=request.find("CommentPercent")
        pe=request.find(",",ps)
        haopingdu=request[ps+17:pe-1]  #str   评论总数
        haopingdu=ch(haopingdu)
        if haopingdu=='':
            haopingdu="NULL"

        #--------------------------------------------------------------------------
        
        index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
        index = open(index_filename, 'a')
        #print(page+ '\t'+ filename+ '\t'+ name+ '\t'+ imgurl+ '\t'+price+ '\t'+ comment+'\t'+haopingdu)
        print(price+ '\t'+ comment+'\t'+haopingdu)
        index.write(page+ '\t'+ filename+ '\t'+ name+ '\t'+ imgurl+ '\t'+price+ '\t'+ comment+'\t'+haopingdu+'\n')
       

        if varLock.acquire():
                            
            crawled.append(page)
            varLock.release()
            
        index.close()

        return 1
    except Exception as e:
        print("get_page")
        print(e)
        
        return 0
   


def working():

    while True:        
        if q.empty():
            return 0
        page = q.get()
        if page not in crawled:
            #print(page) 
            get_page(page)
                         #如果爬取到网页
                # if add_page_to_folder(page, content)==1:     
                #     outlinks = get_all_links(page)
                #     if outlinks!="":  
                #         for link in outlinks:
                #             if count<=max_page:
                #                 q.put(link)
                #                 count+=1                

        q.task_done()
    
start = time.time()

crawled = []
#max_page=int(input("请输入最多爬取的网页数："))
q = queue.Queue()

f = open("item.txt")               # 返回一个文件对象   
line = f.readline()  
#c=0             # 调用文件的 readline()方法   
while line:   
        
    q.put(line[:-1])            # 后面跟 ',' 将忽略换行符   
    #print(line, end = '')    # 在 Python 3 中使用   
    line = f.readline()   


varLock = threading.Lock()
NUM = 50 #并行线程数量

for i in range(NUM):
    t = threading.Thread(target=working)
    t.setDaemon(True)
    t.start()
    
q.join()

end = time.time()
print(end - start)