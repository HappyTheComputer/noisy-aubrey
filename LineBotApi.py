import os
import sys
import tempfile
from flask import abort

from AskGod import random_ask
from DataBaseApi import test_database, add_worker_database, add_fight_field_database

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
        if text.startswith('#神'):
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
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])

@handler.add(FollowEvent)
def handle_follow(event):
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
    line_bot_api.push_message(
        pushTo, pushArr
    )

def check_reply_message_method(msgDict, replyTo):
    replyArr = []
    for var in msgDict.values():
        if var['type'] == 'Text':
            replyArr.append(TextSendMessage(text=var['text']))
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
    elif isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        testDict['0']['text'] = '不要以為你是' + profile.display_name + '就了不起哦！'
        add_worker_database(event.source.user_id)
    elif isinstance(event.source, SourceGroup):
        testDict['0']['text'] = '各位下班了嗎～'
        add_fight_field_database(event.source.group_id)
    else:
        testDict['0']['text'] = "你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。"
    check_reply_message_method(testDict, event.reply_token)