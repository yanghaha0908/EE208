from flask import Flask,render_template,request,redirect,url_for

import sys, os, lucene,re
import cv2
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
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from bs4 import BeautifulSoup
import mySearchFilenotpic#import自定义的搜索功能的文件
import math

INDEX_DIR = "IndexFiles.index"

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

def search(keyword):
    STORE_DIR = "index"
    try:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])#启动Lucene的时候添加
        #print('lucene', lucene.VERSION)
    except:
        vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()#绑定线程
   
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer()#Version.LUCENE_CURRENT)
    # analyzer = StandardAnalyzer()
    # querys = BooleanQuery.Builder()
    result = mySearchFilenotpic.run(searcher, analyzer,keyword)
    del searcher
    vm_env.detachCurrentThread()#销毁线程
    # print(result[1])
    return result


app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def zhu():
    if request.method == 'POST':
        keyword = request.form['keyword']
        return redirect(url_for('result',keyword = keyword))
    return render_template("zhu.html")


@app.route('/im',methods=['POST','GET'])
def im_search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        return redirect(url_for('pic_results',keyword = keyword))
    return render_template("im.html")


@app.route('/result',methods=['GET'])
def result():
    keyword = request.args.get('keyword')
    result = search(keyword)
    return render_template("result.html",keyword=keyword,result=result)


@app.route('/about',methods=['POST','GET'])
def about():
    if request.method == "POST":
        keyword = request.method['keyword']
        return redirect(url_for('imresult',keyword = keyword))
    return render_template('about.html')

@app.route('/result2',methods=['GET'])
def result2():
    keyword = request.args.get('keyword')
    result = search(keyword)
    return render_template("result2.html",keyword=keyword,result=result)


@app.route('/pic_results',methods=['POST','GET'])
def pic_results():
    if request.method == 'POST':
        keyword = request.form['keyword']
        return redirect(url_for('pic_results',keyword = keyword))

    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()#将虚拟机添加到线程，防止搜索程序内存泄露
    keyword = request.args.get('keyword')
    
    #分别以灰度和色彩形式读入图片
    img1 = cv2.imread('pic/'+str(keyword),cv2.IMREAD_COLOR)
    img2 = cv2.imread('pic/'+str(keyword),cv2.IMREAD_GRAYSCALE)
    #得到搜索图片的Hamming码
    vector_p = get_p(img1)
    vector_g = get_gray(img2)
    hamming_code1 = get_Hamming(vector_p)
    hamming_code2 = get_Hamming(vector_g)
    hamming_code = hamming_code1 + hamming_code2
    #图片搜索index
    STORE_DIR = "picindex"
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer()

    query = QueryParser("hamming", analyzer).parse(hamming_code)#进行词法分析，语法分析和语言处理

    scoreDocs = searcher.search(query, 5).scoreDocs #显示排名前5的搜索结果
    pic_li = []
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        pic_li.append([doc.get("name"),doc.get("htmlurl"),doc.get("imgurl")])

    del searcher
    return render_template("pic_results.html",keyword = keyword,pic_li = pic_li)

if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    app.run(debug=True,port=8081)