INDEX_DIR = "IndexFiles.index"
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlencode
import re
import random
import cv2
import sys, os, lucene, threading, time
from datetime import datetime
import jieba #使用结巴分词器
# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
#引用空格分词器 
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
#
#引用BeautifulSoup来过滤html中的标签
from bs4 import BeautifulSoup
#
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
import math


def get_p(img):#得到图像的p维向量的函数(p=12)
    p = []
    h,w,c = img.shape
    for k1 in range(2):
        for k2 in range(2):
            sum_blue = sum_green = sum_red = 0
            for i in range(int(k1*h/2),int((k1+1)*h/2)):
                for j in range(int(k2*w/2),int((k2+1)*w/2)):
                    sum_blue += img[i,j][0]
                    sum_green += img[i,j][1]
                    sum_red += img[i,j][2]
            total_energy = sum_blue + sum_green + sum_red
            blue_rate = float(sum_blue)/float(total_energy)
            green_rate = float(sum_green)/float(total_energy)
            red_rate = float(sum_red)/float(total_energy)
            p.append(blue_rate)
            p.append(green_rate)
            p.append(red_rate)
    for i in range(12):
        p[i] = int(10*p[i])
    return p

def get_gray(img):#得到图像的灰度向量：
    g = [0 for i in range(0,12)]
    h,w = img.shape
    for i in range(h):
        for j in range(w):
            id = img[i,j]
            g[int(id/22)] += 1
    total = sum(g)
    for i in range(0,len(g)):
        if(g[i]/total<0.1):
            g[i] = int(g[i]/total*100)
        else:
            g[i] = int(g[i]/total*10)
    return g

def get_Hamming(p):#得到Hamming码####
    hamming = ''
    for i in p:
        if i==2:
            hamming += '0010'
        elif i==3:
            hamming += '0011'
        elif i==1:
            hamming += '0001'
        elif i==0:
            hamming += '0000'
        elif i==4:
            hamming += '0100'
        elif i==5:
            hamming += '0101'
        elif i==6:
            hamming += '0110'
        elif i==7:
            hamming += '0111'
        elif i==8:
            hamming += '1000'
        elif i==9:
            hamming += '1001'
    return hamming


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):

    def __init__(self, root1, root2,root3, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = WhitespaceAnalyzer()#在jieba分词之后使用空格分词器
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs1(root1, writer)
        self.indexDocs2(root2,writer)
        self.indexDocs3(root3,writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs1(self, root, writer):

        #定义Field的相关属性t1和t2，t1不可索引，t2可以索引
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(False)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        
        id_file = open(root,'r')
        length = len(id_file.readlines())
        id_file.close()
        id_file = open(root,'r')
        for i in range(int(length/2)):
            try:
                line1 = id_file.readline().split('\t')
                line2 = id_file.readline()
                
                img_url = line1[4]#图片地址
                product_name = line1[2]#商品名称
                html_url = line1[0]#商品的html的url
                
                urllib.request.urlretrieve(img_url,'pic/1.jpg')
                img1 = cv2.imread('pic/1.jpg',cv2.IMREAD_COLOR)
                img2 = cv2.imread('pic/1.jpg',cv2.IMREAD_GRAYSCALE)
                vector_p = get_p(img1)
                vector_g = get_gray(img2)
                hamming_code1 = get_Hamming(vector_p)
                hamming_code2 = get_Hamming(vector_g)
                hamming_code = hamming_code1 + hamming_code2
                print('adding',img_url)
                
                doc = Document()
                doc.add(Field('name',product_name,t1))
                doc.add(Field('imgurl',img_url,t1))
                doc.add(Field('htmlurl',html_url,t1))
                doc.add(Field('hamming',hamming_code,t2))
                writer.addDocument(doc)
                os.remove('pic/1.jpg')
            except:
                continue

        id_file.close()


    
    def indexDocs2(self, root, writer):

        #定义Field的相关属性t1和t2，t1不可索引，t2可以索引
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(False)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        
        id_file = open(root,'r',encoding='gbk')
        for i in range(4448):
            try:
                line1 = id_file.readline().split('\t')
                if len(line1)!=7:
                    continue
                else:
                    img_url = 'http:'+line1[3]
                    product_name = line1[2]
                    html_url = line1[0]
                    
                    urllib.request.urlretrieve(img_url,'pic/1.jpg')
                    img1 = cv2.imread('pic/1.jpg',cv2.IMREAD_COLOR)
                    img2 = cv2.imread('pic/1.jpg',cv2.IMREAD_GRAYSCALE)
                    vector_p = get_p(img1)
                    vector_g = get_gray(img2)
                    hamming_code1 = get_Hamming(vector_p)
                    hamming_code2 = get_Hamming(vector_g)
                    hamming_code = hamming_code1 + hamming_code2
                    print('adding',img_url)
                    
                    doc = Document()
                    doc.add(Field('name',product_name,t1))
                    doc.add(Field('imgurl',img_url,t1))
                    doc.add(Field('htmlurl',html_url,t1))
                    doc.add(Field('hamming',hamming_code,t2))
                    writer.addDocument(doc)
                    os.remove('pic/1.jpg')
            except:
                continue

        id_file.close()


    def indexDocs3(self, root, writer):

        #定义Field的相关属性t1和t2，t1不可索引，t2可以索引
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(False)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        
        id_file = open(root,'r')
        length = len(id_file.readlines())
        id_file.close()
        id_file = open(root,'r')
        for i in range(int(length)):
            try:
                line1 = id_file.readline().split('\t')
                if len(line1)!=8:
                    continue
                img_url = line1[4]#图片地址
                product_name = line1[2]#商品名称
                html_url = line1[0]#商品的html的url
                
                urllib.request.urlretrieve(img_url,'pic/1.jpg')
                img1 = cv2.imread('pic/1.jpg',cv2.IMREAD_COLOR)
                img2 = cv2.imread('pic/1.jpg',cv2.IMREAD_GRAYSCALE)
                vector_p = get_p(img1)
                vector_g = get_gray(img2)
                hamming_code1 = get_Hamming(vector_p)
                hamming_code2 = get_Hamming(vector_g)
                hamming_code = hamming_code1 + hamming_code2
                print('adding',img_url)
                
                doc = Document()
                doc.add(Field('name',product_name,t1))
                doc.add(Field('imgurl',img_url,t1))
                doc.add(Field('htmlurl',html_url,t1))
                doc.add(Field('hamming',hamming_code,t2))
                writer.addDocument(doc)
                os.remove('pic/1.jpg')#删除图片
            except:
                continue
            
        id_file.close()


if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('dangdangindex.txt','guomeiindex.txt','snindex.txt',"index")#建立索引
        print('Done')
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e