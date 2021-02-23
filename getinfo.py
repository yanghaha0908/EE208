from urllib.parse import urlencode
import urllib.request
from bs4 import BeautifulSoup
import re
import random
import urllib
user_agent_pool = ['Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; .NET CLR 3.5.30729)','Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; Windows NT 5.1; (R1 1.5); .NET CLR 2.0.50727; InfoPath.1)',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36','Mozilla/5.0 (compatible; MSIE 9.0; AOL 9.7; AOLBuild 4343.19; Windows NT 6.1; WOW64; Trident/5.0; FunWebProducts)',
'Mozilla/4.0 (compatible; MSIE 8.0; AOL 9.5; AOLBuild 4337.43; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.21022; .NET CLR 3.5.30729; .NET CLR 3.0.30618)',
'Mozilla/5.0 (X11; U; Win95; en-US; rv:1.8.1) Gecko/20061125 BonEcho/2.0']
rad = random.randint(0,5)
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
print(header)
url = 'http://product.dangdang.com/1516430471.html'
res = urllib.request.Request(url,headers = header)
res = urllib.request.urlopen(res).read()
res = BeautifulSoup(res)

#商品名称
i1 = res.find('div',{'class':'name_info'})
product_name = i1.contents[3]['title']
print(product_name)
#商品关键词
i2 = res.find('span',{'class':'head_title_name'})
product_keyword = i2['title']

#商品图片
i3 = res.find('a',{'dd_name':"大图"})
product_pic = i3.contents[1]['src'].rstrip('/t').rstrip('/n')
print(product_pic)
#商品价格
i4 = res.find('p',{'id':'dd-price'})
product_cost = float(i4.contents[2])
print(product_cost)