import time
import random
from flask import request
from LineBotApi import check_push_message_method
from DataBaseApi import select_table
from DownloadImg import search_image

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

