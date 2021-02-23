# SJTU EE208

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene

from java.io import File
from java.nio.file import Path
import jieba #使用结巴分词器
#引用空格分词器 
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
#
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version



def price(elem):
    return float(elem[3])

def rank(elem):
    return float(elem[6])

def run(searcher, analyzer,keyword):
    command=keyword
    if command == '':
        return
    

    print ("Searching for:", command)
    command = ' '.join(jieba.cut(command))#对输入的command进行jieba分词
    print(command)
    query = QueryParser("contents", analyzer).parse(command)#进行词法分析，语法分析和语言处理
    scoreDocs = searcher.search(query, 50).scoreDocs #显示排名前50的搜索结果
    print ("%s total matching documents." % len(scoreDocs))

    return_list=[]
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        if float(doc.get("price"))<0:
            continue
        return_list.append((doc.get("name"),doc.get("url"),doc.get("img_url"),doc.get("price"),doc.get("pinglunshu"),doc.get("haopinglv"), doc.get("rank") ))
        # 列表·
    return_to_sort = return_list[:]
    return_to_sortbyrank = return_list[:]
    return_to_sort_down = return_list[:]
    
    return_to_sort.sort(key=price)#按照商品价格升序排序
    return_to_sort_down.sort(key=price,reverse=True)#按照商品评价降序排序
    return_to_sortbyrank.sort(key=rank,reverse=True)#按照商品价格降序排序
    return return_list,return_to_sort,return_to_sortbyrank,return_to_sort_down
 
