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
        temp = t.text.replace('○', '\t').replace('●', '\t')
        chanceDict['poems'].append(temp)
    poem = soup.select("div.fs_poetry_w_text")
    for p in poem:
        chanceDict['poems'].append(p.text)
    
    # detail = soup.find_all("div", class_="fs_box fs_left")
    # for d in detail:
    #     print(d.text)
    print(chanceDict)
    return chanceDict

GameKeyWords = {
    '杯': ['凸凸-沒杯啦！', '平凸-聖杯啦！', '凸平-聖杯啦！', '平平-笑杯啦！'],
    '吉凶': ['大吉大利！', '中吉之戰！', '小吉不嫌棄。', '吉也佳～', '後悔末吉QQ', '凶無大志。', '大凶之兆。'],
    '籤': {
        '六十甲子籤': 60
    },
    'anyothermessage': {
        "11537":[52002734, 52002773],
        "11538":[51626494, 51626533],
        "11539":[52114110, 52114149]
    }
}

def random_ask(askText):
    godAnswer = {
        'type':'',
    }

    for key in GameKeyWords.keys():
        if askText.find(key) >= 0:
            # 亂數回字串
            if type(GameKeyWords[key]) == list:
                godAnswer['type'] = 'Text'
                godAnswer['text'] = random.choice(GameKeyWords[key])
                break
            elif key == '籤':
                pickId = random.randint(1, GameKeyWords[key]['六十甲子籤'])
                godAnswer['type'] = 'Pick'
                godAnswer['pick'] = pick_sixty_years_chance(pickId)
                break
            
    if not godAnswer['type']:
        # 沒有搜到關鍵字都回貼圖
        godAnswer['type'] = 'Sticker'
        package = random.choice(GameKeyWords['anyothermessage'].keys())
        sticker = random.randint(GameKeyWords['anyothermessage'][package][0], GameKeyWords['anyothermessage'][package][1])
        godAnswer['package'] = package
        godAnswer['sticker'] = sticker
    return godAnswer
