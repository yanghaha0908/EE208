import requests
from bs4 import BeautifulSoup
import time
import urllib
import re
import os
import string
import sys
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
class SNProcess():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        self.run()
    def get_html(self, url):
        proxies = random.choice(pro_list)
        
        res = requests.get(url, headers=self.headers,proxies=proxies)
        # res.encoding = 'utf-8'
        return res.text
    # def write_data(self, data):
    #     with open("result.txt", "a+", encoding="utf-8", errors='ignore', newline="") as f:
            # f_csv = csv.writer(f)
            # f_csv.writerow(data)

    #获取评论的总的数量
    def get_comment_num(self, clsid, goods_src):
        src_args = re.findall(r"com/(.*?).html", goods_src)[0]
        key1 = src_args.split("/")[-1]
        #print(key1)
        if clsid:
            url = "https://review.suning.com/ajax/review_count/cluster-"+str(clsid)+\
              "-0000000"+str(key1)+"-0000000000-----satisfy.htm?callback=satisfy"
        else:
            url = "http://review.suning.com/ajax/review_count/general--0000000"+str(key1)+"-0000000000-----satisfy.htm?callback=satisfy"
        #print(url)
        html = self.get_html(url)
        
        fiveStarCount = re.findall(r'"fiveStarCount":(.*?),', html)[0]
        # picFlagCount = re.findall(r'"picFlagCount":(.*?),', html)[0]
        totalCount = re.findall(r'"totalCount":(.*?),', html)[0]
        # againCount = re.findall(r'"againCount":(.*?),', html)[0]
        #print(totalCount,fiveStarCount)
        return totalCount, fiveStarCount

     #获取手机的信息 里面的获取clusterid这个很关键 主要是后面的评论和评论统计数据url构造中都有这个参数
    def get_goods_title(self, url):
        html = self.get_html("https:" + url)
        soup = BeautifulSoup(html, 'lxml')
        # print(html)
        title = soup.find_all('title')[0].get_text()
        clusterId = re.compile(r'"clusterId":"(.*?)"', re.S)
        clusterId_ret = clusterId.findall(html)
        try:
            args0 = soup.find_all("dd", attrs={"class": "r-info"})[0].get_text()
            args1 = soup.find_all("dd", attrs={"class": "r-info"})[1].get_text()
            args2 = soup.find_all("dd", attrs={"class": "r-info"})[2].get_text()
        except:
            args0, args1, args2 = ["无参数"] * 3
        return clusterId_ret[0],title, args0,args1,args2

    #获取手机的价格 手机价格的连接需要自己拼凑
    def get_price_html(self, goods_src):
        try:
            src_args = re.findall(r"com/(.*?).html", goods_src)[0]
            key0 = src_args.split("/")[0]
            key1 = src_args.split("/")[-1]
            price_src = "https://pas.suning.com/nspcsale_0_0000000" + key1 + "_0000000" + key1 + "_" + key0 + "_20_021_0210199_20268_1000267_9264_12113_Z001___R0503002_5.2_0___000030743____0___63960.0_1_01_293006_243505_.html?callback=pcData&_=1606042495463"
            html = self.get_html(price_src)
            #print(price_src)
            price = re.compile(r'"refPrice":"(.*?)"', re.S)
            price_ret = price.findall(html)
            # print(price_ret)
            if price_ret[0] == '':
                price = re.compile(r'"promotionPrice":"(.*?)"', re.S)
                price_ret = price.findall(html)
                # print(price_ret[0])
            if price_ret[0] == '':
                price = re.compile(r'"netPrice":"(.*?)"', re.S)
                price_ret = price.findall(html)
            # price_ret = price.findall(html)
            #print(price_ret[0])
            return price_ret[0]
        except:
            return -1

    #获取手机图片
    def get_img_html(self,url):
        try:
            #print(url)
            html = self.get_html(url)
            #print(html)
            
            soup = BeautifulSoup(html, 'lxml')
            imgdiv = soup.find_all(attrs={'class':'view-img'})
            #print(imgdiv)
            urlres = imgdiv[0].contents[1]['src']
            #print('0',urlres)
            url = "https:"+urlres
            return url
        except:
            return None

     #主页面数据获取  关键函数
    def get_phone_data(self, html):
        soup = BeautifulSoup(html, 'lxml')
        try:
            # li = soup.find_all('ul', attrs={'class': 'general clearfix'})[0].find_all("li")
            li = soup.find_all("li")
            print(len(li))
            for i in range(len(li)):
                try:
                    src = li[i].find_all("a", attrs={"target": "_blank"})[0].get("href")
                    print(src)
                    srcres = "https:"+src
                    comment_num = li[i].find_all("div", attrs={"class": "info-evaluate"})[0].find_all("a")[0].get_text()
                    # print(comment_num)
                    #is_self_support = li[i].find_all("div", attrs={"class": "store-stock"})[0].find_all("a")[0].get_text()
                    # print(is_self_support)
                    price = self.get_price_html(src)
                    # print(price)
                    clusterId, title, args0, args1, args2 = self.get_goods_title(src)
                    # print(title)
                    totalCount,fiveStarCount= self.get_comment_num(clusterId, src)
                    try:
                        rate = float(fiveStarCount)/float(totalCount)
                    except:
                        rate = None
                    # print("imgsrc:",srcres)
                    imgsrc = self.get_img_html(srcres)
                    ret_data = [title, comment_num, price, args0, args1, args2, totalCount,rate,imgsrc]
                    srchtml = self.get_html(srcres)
                    self.add_page_to_folder(srcres,srchtml,ret_data)
                except:
                    print("数据异常")
                    continue
        except:
            print("error")
            pass
    
    def valid_filename(self,s):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in s if c in valid_chars)
        return s

    def add_page_to_folder(self,page, content, ret_data):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
        global dic ##将字典声明为全局变量，为了在后面判断网页是否重复
        content = str(content)
        #print(content)
        index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
        folder = 'html'  # 存放网页的文件夹
        filename = self.valid_filename(page)  # 将网址变成合法的文件名
        if filename in dic:##防止重复网页
            return
        else:
            dic[filename] = page
        index = open(index_filename, 'a',encoding="utf-8")
        #写入文件的顺序为url,文件名,商品名称,商品关键词,商品图片,商品价格,商品评论数,商品好评率
        index.writelines(page + '\t' + filename + '\t' + str(ret_data[0]) + '\t' + str(ret_data[3]) + '\t' + str(ret_data[8])+ '\t' + str(ret_data[2]) +'\t' + str(ret_data[6]) + '\t' + str(ret_data[7]) +'\n')
        print('downloading page %s' % page)
        index.close()
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        f = open(os.path.join(folder, filename), 'w+',encoding="utf-8")
        f.write(content)  # 将网页存入文件
        f.close()


    def run(self):
        a = urllib.parse.quote("智能")
        for i in range(3,50):
            print("第%s页" % i)
            for j in range(4):
            # url = "https://search.suning.com/"+a+"/&iy=0&isNoResult=0&cp=" + str(i)
                url = "https://search.suning.com/emall/searchV1Product.do?keyword="+a+"&ci=0&pg=01&cp="+str((i-1))+"&il=0&st=0&iy=0&adNumber=10&isNoResult=0&n=1&cc=021&paging="+str(j)+"&sub=0"
                print("url",url)
                html = self.get_html(url)
                self.get_phone_data(html)
            # ret_data,srcres  = self.get_phone_data(html)
            # srchtml = self.get_html(srcres)
            # self.add_page_to_folder(srcres,srchtml,ret_data)
if __name__ == "__main__":
    SNProcess()