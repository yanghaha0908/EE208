# EE208
爬虫爬取的苏宁，当当和国美的数据分别存储在snindex.txt,guomeiindex.txt和dangdangindex.txt中。
当当爬虫的代码：当当爬虫.py（getinfo.py和getcomment.py分别为获取商品信息和商品评价的函数，其内容已经全部复制进当当爬虫.py中）
苏宁爬虫代码：suning.py
国美爬虫代码：国美爬虫.py

文字索引建立代码：文字索引建立.py
文字索引：文件夹index
图片索引建立代码：图片索引建立.py
图片索引：文件夹picindex

mySearchFilenotpic.py：用于进行在输入框输入文字的搜索并将返回结果分别以默认排序，价格升序降序，商品评价排序进行返回（在app.py中引用该py文件）
app.py：主程序，网站的Flask框架（8081端口）


文件夹：
layui：网站前端的框架
static：网站前端的框架(以及用到的图片)
pic：要在网站中测试搜索的本地图片集

templates：网页代码：
zhu.html 网站首页
im.html 进行图片搜索的页面
results2.html 从主页点击商品分类或品牌来进行过滤跳转到的页面
result.html 文字搜索结果返回页面
pic_results.html 以图搜图搜索结果返回页面
about.html 小组相关信息页面
