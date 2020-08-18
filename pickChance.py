import requests as rq
from bs4 import BeautifulSoup

GodNameKeys = ['六十甲子籤', '觀音一百籤', '雷雨師一百籤', '保生大帝六十籤', '澎湖天后宮一百籤', '淺草金龍山觀音寺一百籤']

def pick_sixty_years_chance(index):
    godname = '六十甲子籤'
    chanceDict = {
        'url':'',
        'image':'',
        'poems':[],
        'explanation':[]
    }
    chanceDict['url'] = 'http://www.chance.org.tw/籤詩集/%s/籤詩網‧%s__第%02d籤.htm' %(godname, godname, index)
    r = rq.get(chanceDict['url'])
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
            chanceDict['image'] = 'http://www.chance.org.tw/籤詩集/%s/' %godname
            chanceDict['image'] += i['src']
            print(chanceDict['image'])
            break
    # 詩籤文字
    # result = body.find_all("font", face='新細明體')
    # for r in result:
    #     temp = r.text.replace('\t', '').replace('\n', '').replace(' ', '').replace('\r', '\n')
    #     if len(temp) > 0:
    #         chanceDict['poems'].append(temp)
    #         print(temp)
    # print(chanceDict['poems'])
    # details = body.find("p", align="left", style="line-height: 150%")
    # print(details.text)
    # chanceDict['tags'] = details.text.replace('\n', ' ').replace('\u3000', '：')
    # print(chanceDict['tags'])
    # 詳細解籤
    comment = soup.select("p.MsoNormal span")
    poemsSave = False
    explanationSave = False
    for c in comment:
        temp = c.text.replace('\t', '').replace('\n', '').replace(' ', '').replace('\u3000', '').replace('\xa0', '')
        if len(temp) > 0:
            if temp.find('籤詩故事') >= 0:
                poemsSave = False
                explanationSave = False
                break
            elif temp.find('籤詩語譯') >= 0:
                poemsSave = True
                explanationSave = False
                continue
            elif temp.find('籤意分享') >= 0:
                poemsSave = False
                explanationSave = True
                continue
            elif poemsSave:
                print(temp)
                chanceDict['poems'].append(temp)
            elif explanationSave:
                print(temp)
                chanceDict['explanation'].append(temp)
    print(chanceDict)
    return chanceDict

