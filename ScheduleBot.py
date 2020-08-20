import time
import random
from flask import request
from LineBotApi import check_push_message_method
from DataBaseApi import select_table
from DownloadImg import search_image

def good_morning():
    testDict = {
        '0':{
            'type':'Text',
            'text':'認命吧上班囉～'
        },
        '1':{
            'type':'Image',
            'img':'https://i.pinimg.com/originals/15/d6/06/15d606d56054969594bb4cf8e6d32bd9.jpg'
        },
        '2':{
            'type':'Btn',
            'title':'測試標題',
            'fullText':'內文內文內文內文\n內文內文內文內文',
            'minText':'縮圖',
            'btns':{
                '0':{
                    'type':'date',
                    'label':'回撥測試',
                    'postback':'deadline'
                }
            }
        }
    }
    workers = select_table('workers', 'worker_id')
    for w in workers:
        pushTo = w[0]
        if len(pushTo) > 0:
            check_push_message_method(testDict, pushTo)

def greet_worker():
    greetWeekText = [
        '各位社畜加油吧，週一來一寶～', 
        '週二難熬啊，甜心隊長給你加油！', 
        '這週過半啦，週三啊各位！', 
        '今天是雷神之日。', 
        '要放假啦！嗨起來！']
    greetWeekImg = ['Thomas Holland', 'Chris Evans', 'Ryan Reynolds', 'Thor Odinson', 'Robert Downey']
    today=int(time.strftime("%w"))-1
    if today >= 0 and today < 5:
        todayImages = search_image(greetWeekImg[today], 100)
        todayImgFileName = random.choice(todayImages)
        greetDict = {
            '0':{
                'type':'Text',
                'text':greetWeekText[today]
            },
            '1':{
                'type':'Image',
                'img':todayImgFileName
            }
        }
        fields = select_table('fightField', 'group_id')
        for f in fields:
            pushTo = f[0]
            if len(pushTo) > 0:
                check_push_message_method(greetDict, pushTo)

greet_worker()

