import os
import sys

from linebot import (
    LineBotApi
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

# get channel_secret and channel_access_token from your environment variable
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)

# Datebase
import psycopg2

# 連線資料庫
DATABASE_URL = os.environ['DATABASE_URL']

def control_database(commant):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    # 輸入資料庫指令
    cur.execute(commant)
    results=cur.fetchall()
    # 除了Delete之外的指令執行都需要commit()
    conn.commit()
    # 結束連線
    cur.close()
    return results

def assort_event(event):
    text = event.message.text
    if text.startswith('#神'):
        check_text_key(text, event)
    elif text == '測試':
        
        profile = line_bot_api.get_profile(event.source.user_id)
        testText = '%s and %s' %(event.source, profile)
        line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text=testText)
                    ]
        #         )
        # if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup):
        #     profile = line_bot_api.get_profile(event.source.user_id)
        #     if not profile:
        #         line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text="你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。"))
        #     else:
        #         line_bot_api.reply_message(
        #             event.reply_token, [
        #                 TextSendMessage(text='不要以為你是' + profile.display_name + '就了不起哦！')
        #             ]
        #         )
        # else:
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text="啥？"))
    elif text == '資料庫':
        results = control_database('SELECT VERSION()')
        
        replyText = "Database version :\n%s " % results
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=replyText))
    else:
        pass

import random

def check_text_key(text, event):
    if text.find('杯') >= 0:
        askGod = ['凸凸-沒杯啦！', '平凸-聖杯啦！', '凸平-聖杯啦！', '平平-笑杯啦！']
        rand = random.choice(askGod)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=rand))
    elif text.find('運勢') >= 0:
        askGod = ['大吉大利！', '中吉之戰！', '小吉不嫌棄。', '吉也佳～', '後悔末吉QQ', '凶無大志。', '大凶']
        rand = random.choice(askGod)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=rand))
    else:
        # 回官方貼圖
        askGod = {
            "11537":[52002734, 52002773],
            "11538":[51626494, 51626533],
            "11539":[52114110, 52114149]
        }
        package = random.randint(11537, 11539)
        sticker = random.randint(askGod[str(package)][0], askGod[str(package)][1])
        line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=package,
            sticker_id=sticker)
        )
