import requests as rq
from bs4 import BeautifulSoup
import io
import time

# http://www.chance.org.tw/籤詩集/六十甲子籤/籤詩網%E2%80%A7六十甲子籤__第%02d籤.htm
# http://www.chance.org.tw/籤詩集/觀音一百籤/籤詩網%E2%80%A7觀音一百籤__第%03d籤.htm
# http://www.chance.org.tw/籤詩集/雷雨師一百籤/籤詩網%E2%80%A7雷雨師一百籤__第%03d籤.htm
# http://www.chance.org.tw/籤詩集/保生大帝六十籤/籤詩網%E2%80%A7保生大帝六十籤__第%02d籤.htm
# http://www.chance.org.tw/籤詩集/澎湖天后宮一百籤/澎湖天后宮一百籤_第%03d籤.htm
# http://www.chance.org.tw/籤詩集/淺草金龍山觀音寺一百籤/籤詩網%E2%80%A7淺草金龍山觀音寺一百籤__第%03d籤.htm

def get_chance_detail(godname:str, index:int):
    chanceDict = {
        'god':godname, 
        'index':index,
        'image':'',
        'poems':[],
        'tags':'',
        'explanation':[]
    }
    link = 'http://www.chance.org.tw/籤詩集/%s/籤詩網‧%s__第%02d籤.htm' %(godname, godname, index)
    r = rq.get(link)
    r.encoding = 'big5'
    #顯示網頁狀態
    # print(r.status_code)
    #顯示200即為正常
    #通常2開頭為正常
    #開頭為4或5表示錯誤
    soup = BeautifulSoup(r.text,'lxml') #將網頁資料以html.parser
    # titles = soup.select("head title")
    # print(titles)
    # 主體
    body = soup.find("td", valign="top")
    # 圖
    imgs = body.select("a img")
    for i in imgs:
        if i['src'].rfind('.jpg') >= 0:
            chanceDict['image'] = 'http://www.chance.org.tw/' + i['src']
            # print(chanceDict['image'])
            break
    # 詩籤文字
    result = body.find_all("font", face='新細明體')
    for r in result:
        temp = r.text.replace('\t', '').replace('\n', '').replace(' ', '').replace('\r', '\n')
        if len(temp) > 0:
            chanceDict['poems'].append(temp)
            print(temp)
    # print(chanceDict['poems'])
    details = body.find("p", align="left", style="line-height: 150%")
    # print(details.text)
    chanceDict['tags'] = details.text.replace('\n', ' ').replace('\u3000', '：')
    # print(chanceDict['tags'])
    # 詳細解籤
    # comment = body.select("p.MsoNormal span")
    # for c in comment:
    #     print(c.text)
    return chanceDict

GodNameKeys = ['六十甲子籤', '觀音一百籤', '雷雨師一百籤', '保生大帝六十籤', '澎湖天后宮一百籤', '淺草金龍山觀音寺一百籤']
get_chance_detail(GodNameKeys[0], 4)