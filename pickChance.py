import requests as rq
from bs4 import BeautifulSoup

GodNameKeys = ['六十甲子籤', '觀音一百籤', '雷雨師一百籤', '保生大帝六十籤', '澎湖天后宮一百籤', '淺草金龍山觀音寺一百籤']
#
def pick_sixty_years_chance(index):
    godname = '六十甲子籤'
    chanceDict = {
        'url':'',
        'poems':[],
        'explanation':[]
    }
    chanceDict['url'] = 'https://qiangua.temple01.com/qianshi.php?t=fs60&s=%d' %(index)
    r = rq.get(chanceDict['url'])
    # r.encoding = 'big5'
    #顯示網頁狀態
    # print(r.status_code)
    #顯示200即為正常
    #通常2開頭為正常
    #開頭為4或5表示錯誤
    soup = BeautifulSoup(r.text,'lxml') #將網頁資料以html.parser
    title = soup.select("div.fs_poetry_w_top")
    for t in title:
        temp = t.text.replace('\r', '').replace('\t', '').replace('\n', '').replace('\u3000', '')
        chanceDict['poems'].append(temp)
    poem = soup.select("div.fs_poetry_w_text")
    for p in poem:
        chanceDict['poems'].append(p.text)
    
    # detail = soup.find_all("div", class_="fs_box fs_left")
    # for d in detail:
    #     print(d.text)
    print(chanceDict)
    return chanceDict

# pick_sixty_years_chance(19)