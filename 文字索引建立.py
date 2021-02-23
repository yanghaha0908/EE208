# SJTU EE208

INDEX_DIR = "IndexFiles.index"

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


def is_digit(n):
    return n in "0123456789."

def ch(m):
    a=filter(is_digit,list(m))
    a=''.join(list(a))
    return a

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""


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

        
  
        self.indexDocsdd(root1,writer)
        self.indexDocsguomei(root2,writer)
        self.indexDocssn(root3, writer)

        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocsdd(self, root, writer):

        #定义Field的相关属性t1和t2，t1不可索引，t2可以索引
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
            
        id_file = open(root,'r')
        length = len(id_file.readlines())
        id_file.close()
        id_file = open(root,'r')
        c=0
        for i in range(int(length/2)):

            try:
                line1 = id_file.readline().split('\t')
                line2 = id_file.readline().split('\t')
                    
                img_url = line1[4]#图片地址
                product_name = line1[2]#商品名称
                html_url = line1[0]#商品的html的url
                price=line2[0]
                if '-'in price:
                    p=price.find('-')
                    price=price[:p]

                price=ch(price)

                
                # if c>100:
                #     exit(0)
                pinglunshu=ch(line2[1])
                haopinglv=ch(line2[2])



                #print(line2[0],"1",price)                    

                shuxing= line1[2]                   
                text = ' '.join((jieba.cut(shuxing)))
                rank=float(pinglunshu)*0.8+float(pinglunshu)*float(haopinglv)*0.2*0.01
                

                print(c,'adding',html_url)
                c+=1
                doc = Document()
                doc.add(Field("name", product_name, t1))     
                doc.add(Field("url",html_url,t1))
                doc.add(Field("img_url",img_url,t1))

                doc.add(Field("price",price,t1))
                doc.add(Field("pinglunshu",pinglunshu,t1))
                doc.add(Field("haopinglv",haopinglv,t1))
                doc.add(Field("rank",rank,t1))

                if len(text) > 0:#
                    doc.add(Field("contents", text, t2))#
                else:
                    print("warning: no content in %s" % filename)
                writer.addDocument(doc)
            except Exception as e:
                print("Failed in indexDocs:", e)
                print(price,haopinglv,pinglunshu)
        id_file.close()

    def indexDocsguomei(self, root, writer):

        #定义Field的相关属性t1和t2，t1不分词并且完全储存内容，t2分词但不完全储存内容
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        
        ##将进行爬虫过程中存入index.txt中的文件名与其对应的url以键值对的形式存成一个字典:
        c=0
        #file = open(root,'r',encoding='gbk')
        file = open(root,'r',encoding='gb18030',errors='ignore')
        for line in file.readlines():
            try:
                line1 = line.split('\t')
                if len(line1)!=7:
                    continue
                else:
                    img_url = 'http:'+line1[3]
                    product_name = line1[2]                    
                    html_url = line1[0]
                    price=line1[4]
                    pinglunshu=line1[5]
                    haopinglv=line1[6][:-1]

                    rank=float(pinglunshu)*0.8+float(pinglunshu)*float(haopinglv)*0.2*0.01

                    shuxing= line1[2]                   
                    text = ' '.join((jieba.cut(shuxing)))


                    print(c,'adding',html_url)
                    c+=1
                    doc = Document()
                    doc.add(Field("name", product_name, t1))     
                    doc.add(Field("url",html_url,t1))
                    doc.add(Field("img_url",img_url,t1))
                    doc.add(Field("price",price,t1))
                    doc.add(Field("pinglunshu",pinglunshu,t1))
                    doc.add(Field("haopinglv",haopinglv,t1))
                    doc.add(Field("rank",rank,t1))

                    if len(text) > 0:#
                        doc.add(Field("contents", text, t2))#
                    else:
                        print("warning: no content in %s" % filename)
                    writer.addDocument(doc)

            except Exception as e:
                print("Failed in indexDocs:", e)

        file.close()

    def indexDocssn(self, root, writer):

        #定义Field的相关属性t1和t2，t1不可索引，t2可以索引
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
            
        id_file = open(root,'r')
        length = len(id_file.readlines())
        id_file.close()
        id_file = open(root,'r')

        c=0
        for i in range(int(length)):

            try:
                line1 = id_file.readline().split('\t')
                if len(line1)!=8:
                    continue
                html_url = line1[0]#商品的html的url                    
                img_url = line1[4]#图片地址
                product_name = line1[2]#商品名称

                shuxing= line1[2]+line1[3]                  
                text = ' '.join((jieba.cut(shuxing)))

                price=line1[5]
                pinglunshu=ch(line1[6])
                haopinglv=ch(line1[7])
                rank=float(pinglunshu)*0.8+float(pinglunshu)*float(haopinglv)*0.2  #苏宁的不用x0.01

                

                print(c,'adding',html_url)
                c+=1
                doc = Document()
                doc.add(Field("name", product_name, t1))     
                doc.add(Field("url",html_url,t1))
                doc.add(Field("img_url",img_url,t1))
                doc.add(Field("price",price,t1))
                doc.add(Field("pinglunshu",pinglunshu,t1))
                doc.add(Field("haopinglv",haopinglv,t1))
                doc.add(Field("rank",rank,t1))

                if len(text) > 0:#
                    #print(text)
                    #exit(0)
                    doc.add(Field("contents", text, t2))#
                else:
                    print("warning: no content in %s" % filename)


                writer.addDocument(doc)

            except Exception as e:
                print("Failed in indexDocs:", e)
                print(price,haopinglv,pinglunshu)
            
                
                
        id_file.close()        
        
        ##
       

if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('dangdangindex.txt','guomeiindex.txt','snindex.txt',"index")#建立索引
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        #raise e
