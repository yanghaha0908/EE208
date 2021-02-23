#得到好评率和好评数的程序
from urllib.parse import urlencode
import urllib.request
from bs4 import BeautifulSoup
import re
import json

url = 'http://product.dangdang.com/1620965943.html'
main_res = urllib.request.urlopen(url).read()
main_res = BeautifulSoup(main_res)

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

res = urllib.request.urlopen(aj)
res = BeautifulSoup(res)
res = str(res)
li1 = res.split('"list":')
li2 = li1[1].split(',"html"')
re = li2[0]+'}'
re = json.loads(re)
total_comment = float(re.get('summary').get('total_comment_num'))
good_rate = float(re.get('summary').get('goodRate'))
print(total_comment,good_rate)