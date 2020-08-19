import os
import sys
import random

import pickChance

from linebot import (
    WebhookHandler, LineBotApi
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

class LineBotApi():
    def callback(self, body, signature):
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
    def handle_text_message(self, event):
        text = event.message.text
        if isinstance(event.source, SourceUser):
            self.ask_god_message(text, event)
        elif isinstance(event.source, SourceRoom) or isinstance(event.source, SourceGroup):
            if text.startswith('#神'):
                self.ask_god_message(text, event)
            else:
                self.test_message(text, event)
        else:
            self.test_message(text, event)

    @handler.add(MessageEvent, message=LocationMessage)
    def handle_location_message(self, event):
        line_bot_api.reply_message(
            event.reply_token,
            LocationSendMessage(
                title='Location', address=event.message.address,
                latitude=event.message.latitude, longitude=event.message.longitude
            )
        )

    @handler.add(MessageEvent, message=StickerMessage)
    def handle_sticker_message(self, event):
        self.ask_god_message('', event)
    
    # Other Message Type
    @handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
    def handle_content_message(self, event):
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
    def handle_file_message(self, event):
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
    def handle_follow(self, event):
        print("Got Follow event:" + event.source.user_id)
        # app.logger.info("Got Follow event:" + event.source.user_id)

    @handler.add(UnfollowEvent)
    def handle_unfollow(self, event):
        print("Got Unfollow event:" + event.source.user_id)
        # app.logger.info("Got Unfollow event:" + event.source.user_id)

    @handler.add(JoinEvent)
    def handle_join(self, event):
        print('Joined this ' + event.source.type)
        # app.logger.info('Joined this ' + event.source.type)

    @handler.add(LeaveEvent)
    def handle_leave(self, ):
        print("Got leave event")
        # app.logger.info("Got leave event")

    @handler.add(PostbackEvent)
    def handle_postback(self, event):
        if event.postback.data == 'ping':
            self.reply_text_message('pong', event)
        elif event.postback.data == 'datetime_postback':
            self.reply_text_message(event.postback.params['datetime'], event)
        elif event.postback.data == 'date_postback':
            self.reply_text_message(event.postback.params['date'], event)
    
    @handler.add(BeaconEvent)
    def handle_beacon(self, event):
        print('Got beacon event. hwid={}, device_message(hex string)={}'.format(event.beacon.hwid, event.beacon.dm))
        # app.logger.info('Got beacon event. hwid={}, device_message(hex string)={}'.format(event.beacon.hwid, event.beacon.dm))

    @handler.add(MemberJoinedEvent)
    def handle_member_joined(self, event):
        print('Got memberJoined event. event={}'.format(event))
        # app.logger.info('Got memberJoined event. event={}'.format(event))

    @handler.add(MemberLeftEvent)
    def handle_member_left(self, event):
        print("Got memberLeft event")
        # app.logger.info("Got memberLeft event")

    def reply_text_message(self, replyText, event):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=replyText))
    
    def test_message(self, text, event):
        if text == '測試':
            if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup):
                profile = line_bot_api.get_profile(event.source.user_id)
                self.reply_text_message('不要以為你是' + profile.display_name + '就了不起哦！', event)
            else:
                self.reply_text_message("你是誰啊？媽媽說過不能跟陌生人說話，加好友再來戰。", event)

        elif text == '資料庫':
            results = control_database('SELECT VERSION()')
            
            replyText = "Database version :\n%s " % results
            self.reply_text_message(replyText, event)

    def ask_god_message(self, text, event):
        if text.find('杯') >= 0:
            askGod = ['凸凸-沒杯啦！', '平凸-聖杯啦！', '凸平-聖杯啦！', '平平-笑杯啦！']
            rand = random.choice(askGod)
            self.reply_text_message(rand, event)
        elif text.find('吉凶') >= 0:
            askGod = ['大吉大利！', '中吉之戰！', '小吉不嫌棄。', '吉也佳～', '後悔末吉QQ', '凶無大志。', '大凶之兆。']
            rand = random.choice(askGod)
            self.reply_text_message(rand, event)
        elif text.find('籤') >= 0:
            pickId = random.randint(1, 60)
            chance = pickChance.pick_sixty_years_chance(pickId)
            # print(chance)
            pick_template = ButtonsTemplate(
                title=chance['poems'][0] + chance['poems'][1] + chance['poems'][2], 
                text=chance['poems'][3], 
                actions=[
                    URIAction(label='解籤', uri=chance['url'])
                ])
            pick_message = TemplateSendMessage(
                alt_text=chance['poems'][0] + chance['poems'][1], template=pick_template)
            line_bot_api.reply_message(event.reply_token, pick_message)
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
                    sticker_id=sticker
                    )
                )