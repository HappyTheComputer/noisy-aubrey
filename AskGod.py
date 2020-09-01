import random
import execjs
import requests as rq
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

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
    # print(chanceDict)
    return chanceDict

GameKeyWords = {
    '吉凶': ['大吉大利！', '中吉之戰！', '小吉不嫌棄。', '吉也佳～', '後悔末吉QQ', '凶無大志。', '大凶之兆。'],
    '籤': {
        '六十甲子籤': 60
    },
    'anyothermessage': {
        'list':[11537, 11538, 11539],
        "11537":[52002734, 52002773],
        "11538":[51626494, 51626533],
        "11539":[52114110, 52114149]
    }
}

def random_ask(askText):
    godAnswer = {
        '0':{
            'type':'',
        }
    }

    for key in GameKeyWords.keys():
        if askText.find(key) >= 0:
            # 亂數回字串
            if type(GameKeyWords[key]) == list:
                godAnswer['0']['type'] = 'Text'
                godAnswer['0']['text'] = random.choice(GameKeyWords[key])
                break
            elif key == '籤':
                # 詩籤本體
                godAnswer['0']['type'] = 'Btn'
                pickId = random.randint(1, GameKeyWords[key]['六十甲子籤'])
                chance = pick_sixty_years_chance(pickId)
                godAnswer['0']['title'] = ''.join(chance['poems'][0:3])
                godAnswer['0']['fullText'] = chance['poems'][3]
                godAnswer['0']['minText'] = ''.join(chance['poems'][0:2])
                godAnswer['0']['btns'] = {
                    '0':{
                        'type':'url',
                        'label':'解籤',
                        'content':chance['url']
                    }
                }
                break
                
    if askText.find('卦') >= 0:
        godAnswer['0'] = bugua()
        godAnswer['0']['type'] = 'Bugua'
    elif askText.find('杯') >= 0:
        godAnswer['0'] = toss()
        godAnswer['0']['type'] = 'Toss'

    if not godAnswer['0']['type']:
        # 沒有搜到關鍵字都回貼圖
        godAnswer['0']['type'] = 'Sticker'
        package = random.choice(GameKeyWords['anyothermessage']['list'])
        sticker = random.randint(GameKeyWords['anyothermessage'][str(package)][0], GameKeyWords['anyothermessage'][str(package)][1])
        godAnswer['0']['package'] = package
        godAnswer['0']['sticker'] = sticker
    return godAnswer

def toss():
    tossDict = {
        'img':[],
        'title':'',
        'url':'',
        'btn_word':''
    }
    tossDict['url'] = 'https://tw.piliapp.com/static/s3/apps/random/blocks/'
    tossDict['btn_word'] = '擲筊解説'
    tossResult = ''
    for i in range(2):
        tossKey = random.choice(['p', 'n'])
        tossResult += tossKey
        tossDict['img'].append(tossDict['url'] + tossKey + '.png')
    responsWords = {
        'pp':'笑杯啦！',
        'pn':'聖杯啦！',
        'np':'聖杯啦！',
        'nn':'沒杯啦！'
    }
    tossDict['title'] = responsWords[tossResult]
    return tossDict

def bugua():
    buguaDict = {
        'url':'',
        'img':[],
        'title':'',
        'explanation':''
    }

    ua = UserAgent().random
    url = 'https://www.eee-learning.com/eeeApp/'
    buguaMethod = 'app.js'
    r = rq.get(url + buguaMethod, headers={ 'User-Agent': ua })
    r.encoding = 'utf-8'
    jscode = r.text.replace("document.write", "return ")
    bugue = execjs.compile(jscode)
    result = bugue.call("bugua")
    soup = BeautifulSoup(result, 'lxml')
    imgs = soup.select('img')
    for i in imgs:
        buguaDict['img'].append(url + i['src'])
        # print(i['src'])
    link = soup.find("a")
    buguaDict['url'] = url + link['href']
    # print(link['href'])
    words = soup.find("strong").text
    findpos = words.find('：')
    buguaDict['title'] = words[:findpos].replace('\u3000', '')
    buguaDict['explanation'] = words[findpos+1:]
    buguaDict['btn_word'] = '解卦'
    # print(word.text)
    return buguaDict