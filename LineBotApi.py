import os
import sys

from AskGod import random_ask
from DataBaseApi import control_database

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

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

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
        ask_god_message(text, event)
    elif isinstance(event.source, SourceRoom) or isinstance(event.source, SourceGroup):
        if text.startswith('#神'):
            ask_god_message(text, event)
        else:
            test_message(text, event)
    else:
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
    if event.postback.data == 'ping':
        reply_text_message('pong', event)
    elif event.postback.data == 'datetime_postback':
        reply_text_message(event.postback.params['datetime'], event)
    elif event.postback.data == 'date_postback':
        reply_text_message(event.postback.params['date'], event)

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

def reply_text_message(replyText, event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replyText))

def test_message(text, event):
    if text == '測試':
        if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup):
            profile = line_bot_api.get_profile(event.source.user_id)
            reply_text_message('不要以為你是' + profile.display_name + '就了不起哦！', event)
        else:
            reply_text_message("你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。", event)

    elif text == '資料庫':
        results = control_database('SELECT VERSION()')
        
        replyText = "Database version :\n%s " % results
        reply_text_message(replyText, event)

def ask_god_message(text, event):
    godAnswer = random_ask(text)
    if godAnswer['type'] == 'Text':
        reply_text_message(godAnswer['text'], event)
    elif godAnswer['type'] == 'Sticker':
        line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(
                package_id=godAnswer['package'],
                sticker_id=godAnswer['sticker']
                )
            )
    elif godAnswer['type'] == 'Pick':
        titleText = godAnswer['pick']['poems'][0] + godAnswer['pick']['poems'][1] + godAnswer['pick']['poems'][2]
        poemsText = godAnswer['pick']['poems'][3]
        minText = godAnswer['pick']['poems'][0] + godAnswer['pick']['poems'][1]
        pick_template = ButtonsTemplate(
            title=titleText, 
            text=poemsText, 
            actions=[
                URIAction(label='解籤', uri=godAnswer['pick']['url'])
            ])
        pick_message = TemplateSendMessage(
            alt_text=minText, template=pick_template)
        line_bot_api.reply_message(event.reply_token, pick_message)