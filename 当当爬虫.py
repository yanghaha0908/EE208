import threading
import queue
import time
import os
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
import random

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

def get_page(page):#得到页面内容的函数
    time.sleep(0.1)
    proxy_handler = urllib.request.ProxyHandler(random.choice(pro_list))
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    try: #进行异常处理，防止访问一个网页时超时导致程序无法正常运行
        con = urllib.request.Request(page,headers = header)
        con = urllib.request.urlopen(con,timeout=3).read()
        soup = BeautifulSoup(con)
    except Exception:
        return '爬取该网页时超时' 
    return soup


def get_all_links(content,page):
    links = []
    if content != '爬取该网页时超时':
        for i in content.findAll('a',{'href':re.compile('^http|^/')}): #findAll找到网页中所有的相对和绝对地址
            links.append(urllib.parse.urljoin(page,i.get('href','')))  #将地址补全并加入到links中
    return links

def get_comment(url,content):
    try:
        if content != '爬取该网页时超时':
            main_res = content
            url_a1 = 'http://product.dangdang.com/index.php?'
            r = 'comment2Flist'
            productId = re.findall(r'"productId":"(.*?)"',str(main_res))
            productId_str = ''.join(productId)
            catagoryPath = re.findall(r'"categoryPath":"(.*?)"',str(main_res))
            catagoryPath_str = ''.join(catagoryPath)
            mainProductId = re.findall(r'"mainProductId":"(.*?)"',str(main_res))
            mainProductId_str = ''.join(mainProductId)
            mediumId = re.findall(r'"mediumId":"(.*?)"',str(main_res))
            mediumId_str = ''.join(mediumId)
            pageIndex = '1'
            sortType = '1'
            filterType = '1'
            isSystem = '1'
            tagId = '0'
            tagFilterCount = '0'
            template = 'mall'
            parm = {
                'r':r,
                'productId':productId_str,
                'catagoryPath':catagoryPath_str,
                'mainProductId':mainProductId_str,
                'mediumId':mediumId_str,
                'pageIndex':pageIndex,
                'sortType':sortType,
                'filterType':filterType,
                'isSystem':isSystem,
                'tagId':tagId,
                'tagFilterCount':tagFilterCount,
                'template':template
            }
            ajax_url = url_a1 + urlencode(parm)
            aj = ajax_url.replace('comment','comment%')

            header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
            res = urllib.request.Request(aj,headers=header)
            res = urllib.request.urlopen(res)
            res = BeautifulSoup(res)
            res = str(res)
            li1 = res.split('"list":')
            li2 = li1[1].split(',"html"')
            result = li2[0]+'}'
            result = json.loads(result)
            total_comment = float(result.get('summary').get('total_comment_num'))
            good_rate = float(result.get('summary').get('goodRate'))
            li = [total_comment,good_rate]
            return li
    except:
        return [0,0]

def get_info(url,content):
    if content != '爬取该网页时超时':
        res = content

        #商品名称
        i1 = res.find('div',{'class':'name_info'})
        product_name = i1.contents[3]['title']
        
        #商品关键词
        i2 = res.find('span',{'class':'head_title_name'})
        product_keyword = i2['title']
        if(len(product_keyword)<=3):
            product_keyword = 'NU'
        #商品图片
        i3 = res.find('a',{'dd_name':"大图"})
        product_pic = i3.contents[1]['src'].rstrip('/t').rstrip('/n')
        
        #商品价格
        i4 = res.find('p',{'id':'dd-price'})
        product_cost = i4.contents[2].lstrip('/n').lstrip('/t')
        
        li = [product_name,product_keyword,product_pic,product_cost]
        return li


def add_page_to_folder(page, content, info_li, comment_li):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
        global dic ##将字典声明为全局变量，为了在后面判断网页是否重复
        content = str(content)
        index_filename = 'index6.txt'  # index.txt中每行是'网址 对应的文件名'
        folder = 'html6'  # 存放网页的文件夹
        filename = valid_filename(page)  # 将网址变成合法的文件名
        if filename in dic:##防止重复网页
            return
        else:
            dic[filename] = page
        index = open(index_filename, 'a')
        #写入文件的顺序为url,文件名,商品名称,商品关键词,商品图片,商品价格,商品评论数,商品好评率
        index.writelines(page + '\t' + filename + '\t' + str(info_li[0]) + '\t' + str(info_li[1]) + '\t' + str(info_li[2])+ '\t' + str(info_li[3]) +'\t' + str(comment_li[0]) + '\t' + str(comment_li[1]) +'\n')
        print('downloading page %s' % page)
        index.close()
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        f = open(os.path.join(folder, filename), 'w')
        f.write(content)  # 将网页存入文件
        f.close()



    
#q = queue.Queue()
def working():
    for i in range(21,50):
        page = 'http://category.dangdang.com/pg{}-cid4006497.html'.format(str(i+1))
        content = get_page(page)
        outlinks = get_all_links(content,page)
        for link in outlinks:
            try:
                if 'product' in link and link.endswith('html'):
                    link_content = get_page(link)
                    comment_li = get_comment(link,link_content)
                    info_li = get_info(link,link_content)
                    add_page_to_folder(link, link_content, info_li, comment_li)
            except:
                continue


start = time.time()
#NUM = 4 #线程数

working()
#
#thread_list = []#创建一个储存线程的列表
#for i in range(NUM):
    #t = threading.Thread(target=working(i))
    #thread_list.append(t)
#for t in thread_list:
    #t.setDaemon(True)#设置守护线程
    #t.start()
#for t in thread_list:
    #t.join()#阻塞直到所有线程结束
end = time.time() 
print(end - start) #记录主程序运行需要的时间
