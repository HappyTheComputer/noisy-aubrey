import os
import sys
import tempfile
from flask import abort, request
from AskGod import random_ask
from DataBaseApi import test_database

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
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
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET or LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
master_user_id = os.getenv('MasterUserID', None)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def linebotcallback(body, signature):
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if isinstance(event.source, SourceUser):
        if text.startswith('測試'):
            test_message(text, event)
        else:
            godAnswer = random_ask(text)
            check_reply_message_method(godAnswer, event.reply_token)
    elif isinstance(event.source, SourceRoom) or isinstance(event.source, SourceGroup):
        if text.startswith('阿比'):
            godAnswer = random_ask(text)
            check_reply_message_method(godAnswer, event.reply_token)
        elif text.startswith('測試'):
            test_message(text, event)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print(event.message.package_id, event.message.sticker_id)

# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    print('sand some content')

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    print('sand some file')

@handler.add(FollowEvent)
def handle_follow(event):
    say_hello_message(event)
    print("Got Follow event:" + event.source.user_id)
    # app.logger.info("Got Follow event:" + event.source.user_id)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print("Got Unfollow event:" + event.source.user_id)
    # app.logger.info("Got Unfollow event:" + event.source.user_id)

@handler.add(JoinEvent)
def handle_join(event):
    print('Joined this ' + event.source.type)
    # app.logger.info('Joined this ' + event.source.type)

@handler.add(LeaveEvent)
def handle_leave():
    print("Got leave event")
    # app.logger.info("Got leave event")

@handler.add(PostbackEvent)
def handle_postback(event):
    # 使用者使用postback回送的參數會在這邊接收
    print('postback', event.postback)
    if event.postback.data == '測試':
        testDict = {
            '0':{
                'type':'Text',
                'text':'測試回撥！'
            }
        }
        check_reply_message_method(testDict, event.reply_token)
    elif event.postback.data == 'deadline':
        dateDict = {
            '0':{ 'type':'Text' }
        }
        timeType = ['date', 'time', 'datetime']
        for t in timeType:
            if t in event.postback.params:
                dateDict['0']['text'] = event.postback.params[t]
                break
        check_reply_message_method(dateDict, event.reply_token)

@handler.add(BeaconEvent)
def handle_beacon(event):
    print('Got beacon event. hwid={}, device_message(hex string)={}'.format(event.beacon.hwid, event.beacon.dm))
    # app.logger.info('Got beacon event. hwid={}, device_message(hex string)={}'.format(event.beacon.hwid, event.beacon.dm))

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    print('Got memberJoined event. event={}'.format(event))
    # app.logger.info('Got memberJoined event. event={}'.format(event))

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    print("Got memberLeft event")
    # app.logger.info("Got memberLeft event")

def check_push_message_method(msgDict, pushTo):
    pushArr = []
    for var in msgDict.values():
        if var['type'] == 'Text':
            pushArr.append(TextSendMessage(text=var['text']))
        elif var['type'] == 'Image':
            pushArr.append(ImageSendMessage(var['img'], var['img']))
        elif var['type'] == 'Btn':
            btn_template = ButtonsTemplate(
            title=var['title'], 
            text=var['fullText'], 
            actions=get_button_template_message(var['btns']))
            pushArr.append(TemplateSendMessage(
                alt_text=var['minText'], template=btn_template))
        elif var['type'] == 'Bugua':
            get_bugua_flex_message(var, pushTo, False)
        elif var['type'] == 'Toss':
            get_toss_flex_message(var, pushTo, False)
    if len(pushArr) > 0:
        line_bot_api.push_message(pushTo, pushArr)

def check_reply_message_method(msgDict, replyTo):
    replyArr = []
    for var in msgDict.values():
        if var['type'] == 'Text':
            replyArr.append(TextSendMessage(text=var['text']))
        elif var['type'] == 'Image':
            replyArr.append(ImageSendMessage(var['img'], var['img']))
        elif var['type'] == 'Sticker':
            replyArr.append(StickerSendMessage(package_id=var['package'], sticker_id=var['sticker']))
        elif var['type'] == 'Btn':
            # print(var)
            btn_template = ButtonsTemplate(
            title=var['title'], 
            text=var['fullText'], 
            actions=get_button_template_message(var['btns']))
            replyArr.append(TemplateSendMessage(
                alt_text=var['minText'], template=btn_template))
        elif var['type'] == 'Bugua':
            get_bugua_flex_message(var, replyTo)
        elif var['type'] == 'Toss':
            get_toss_flex_message(var, replyTo)
    if len(replyArr) > 0:
        line_bot_api.reply_message(replyTo, replyArr)

def get_button_template_message(actionsDict):
    actionArr = []
    for a in actionsDict.values():
        if a['type'] == 'url':
            actionArr.append(URIAction(label=a['label'], uri=a['content']))
        elif a['type'] == 'date' or a['type'] == 'time' or a['type'] == 'datetime':
            actionArr.append(DatetimePickerAction(label=a['label'], data=a['postback'], mode=a['type']))
        else:
            actionArr.append(MessageAction(label=a['label'], text=a['content']))
    return actionArr
    
def test_message(text, event):
    testDict = {
        '0':{
            'type': 'Text',
        }
    }
    if text.find('資料庫') >= 0:
        testDict['0']['text'] = test_database()
    elif text.find('招呼') >= 0:
        from DownloadImg import search_image
        testDict['0']['text'] = '你以為這麼簡單就可以測試成功嗎？'
        imgFileName = search_image('貓')[0]
        testDict['1'] = {
            'type':'Image',
            'img':imgFileName
        }
    elif isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        testDict['0']['text'] = '不要以為你是' + profile.display_name + '就了不起哦！'
    elif isinstance(event.source, SourceGroup):
        testDict['0']['text'] = '各位下班了嗎～'
    else:
        testDict['0']['text'] = "你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。"
    check_reply_message_method(testDict, event.reply_token)

def say_hello_message(event):
    helloDict = {
        '0': {
            'type':'Text',
            'text':'你要想清楚，成為我好友也不會對你比較好哦！我這個人很簡單，現在就讓我們先把話說清楚。'
        },
        '1': {
            'type':'Text',
            'text':'只有你跟我的時候，我一定不會冷落你這是我的原則，不信你可以試試。用擲筊『杯』、『吉凶』或卜『卦』我會幫你占卜，説『籤』的話我會幫你抽一支六十甲子籤。'
        },
        '2': {
            'type':'Text',
            'text':'但是我在其他人面前會緊張，在群組裡要找我幫忙要先喊『阿比』我才會知道你找我。'
        },
        '3': {
            'type':'Text',
            'text':'就這樣，那麼現在你想跟我聊什麼呢？'
        }
    }
    check_reply_message_method(helloDict, event.reply_token)

def get_toss_flex_message(megDict, to, reply = True):
    bubble = BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            layout='baseline',
            margin='md',
            contents=[
                TextComponent(text=megDict['title'], weight='bold', size='xl'),
            ]
        ),
        body=BoxComponent(
            layout='horizontal',
            margin='sm',
            spacing='sm',
            contents=[
                ImageComponent(
                    size='sm',
                    url=megDict['img'][0],
                ),
                ImageComponent(
                    size='sm',
                    url=megDict['img'][1],
                ),
            ]
        ),
        footer=BoxComponent(
            layout='vertical',
            spacing='sm',
            contents=[                
                SeparatorComponent(),
                ButtonComponent(
                    style='link',
                    height='sm',
                    action=URIAction(label=megDict['btn_word'], uri=megDict['url'])
                )
            ]
        ),
    )
    message = FlexSendMessage(alt_text=megDict['title'], contents=bubble)
    if reply:
        line_bot_api.reply_message(to, message)
    else:
        line_bot_api.push_message(to, message)

def get_bugua_flex_message(megDict, to, reply = True):
    bubble = BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            layout='baseline',
            margin='md',
            contents=[
                TextComponent(text=megDict['title'], weight='bold', size='xl'),
            ]
        ),
        body=BoxComponent(
            layout='horizontal',
            margin='sm',
            spacing='sm',
            contents=[
                ImageComponent(
                    size='sm',
                    url=megDict['img'][1],
                ),
                TextComponent(
                        text=megDict['explanation'],
                        wrap=True,
                        color='#666666',
                        size='sm',
                        flex=5
                    ),
            ]
        ),
        footer=BoxComponent(
            layout='vertical',
            spacing='sm',
            contents=[                
                SeparatorComponent(),
                ButtonComponent(
                    style='link',
                    height='sm',
                    action=URIAction(label=megDict['btn_word'], uri=megDict['url'])
                )
            ]
        ),
    )
    message = FlexSendMessage(alt_text=megDict['title'], contents=bubble)
    if reply:
        line_bot_api.reply_message(to, message)
    else:
        line_bot_api.push_message(to, message)