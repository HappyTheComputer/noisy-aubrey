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
    if isinstance(event.source, SourceUser):
        ask_god_function(text, event)
    elif isinstance(event.source, SourceRoom) or isinstance(event.source, SourceGroup):
        if text.startswith('#神'):
            ask_god_function(text, event)
        else:
            test_some_function(text, event)
    else:
        test_some_function(text, event)
        
import random

def test_some_function(text, event):
    if text == '測試':
        if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='不要以為你是' + profile.display_name + '就了不起哦！')
                    ]
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。"))
    elif text == '資料庫':
        results = control_database('SELECT VERSION()')
        
        replyText = "Database version :\n%s " % results
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=replyText))

import pickChance

def ask_god_function(text, event):
    if text.find('杯') >= 0:
        askGod = ['凸凸-沒杯啦！', '平凸-聖杯啦！', '凸平-聖杯啦！', '平平-笑杯啦！']
        rand = random.choice(askGod)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=rand))
    elif text.find('運勢') >= 0:
        askGod = ['大吉大利！', '中吉之戰！', '小吉不嫌棄。', '吉也佳～', '後悔末吉QQ', '凶無大志。', '大凶之兆。']
        rand = random.choice(askGod)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=rand))
    elif text.find('籤') >= 0:
        pikeId = random.randint(1, 60)
        chance = pickChance.pick_sixty_years_chance(pikeId)
        # 
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
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
