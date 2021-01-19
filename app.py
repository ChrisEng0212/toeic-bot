from flask import Flask, request, abort, render_template, url_for, flash, redirect, jsonify
from datetime import datetime, timedelta
import json
import os
import ast
import time
import redis

try:
    from meta import DEBUG, channel_access_token, channel_secret, redis_pw, SECRET_KEY

except:
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = False
    channel_access_token = os.environ['channel_access_token']
    channel_secret = os.environ['channel_secret']
    redis_pw = os.environ['redis_pw']


from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

r = redis.Redis(
    host = 'redis-11262.c54.ap-northeast-1-2.ec2.cloud.redislabs.com',
    port = 11262,
    password = redis_pw,
    decode_responses = True # get python freiendlt format
)

# print(r)


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Channel Access Token
line_bot_api = LineBotApi(channel_access_token)
# Channel Secret
handler = WebhookHandler(channel_secret)

parser = WebhookParser(channel_secret)


@app.route("/login/<string:pw>", methods=['GET','POST'])
def login(pw):
    print('LOGIN')

    if pw == 'pw':
        return redirect (url_for('data'))
    else:
        return 'Cannot login'

''' UI pages '''

@app.route('/')
def home():
    data = {}

    for k in r.keys():
        data[k] = r.hgetall(k)

    print(data)

    return render_template('/home.html', data=data)

@app.route('/data')
def data():
    return 'Data'



''' Line Bot Actions '''

@app.route('/text/<string:tx>')
def text(tx):
    try:
        line_bot_api.multicast(['U2dc560609e55883a4d869c88c0d912e7'], TextSendMessage(text=tx))
        # max 150 recipients
        # what if recipient has blocked or deleted bot??
    except LineBotApiError as e:
        abort(400)
    return tx

@app.route('/set/<string:tx>')
def setString(tx):
    try:
        line_bot_api.multicast(['U2dc560609e55883a4d869c88c0d912e7', 'U2dc081c2670e8322666ca4d890df6562'], TextSendMessage(text=tx))
        # max 150 recipients
        # what if recipient has blocked or deleted bot??
    except LineBotApiError as e:
        abort(400)
    return tx


def message_list(arg, info):

    if arg == "welcome":
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG'
        )
        message1 = TextSendMessage(text= 'Hi ' + info + '. Welcome to TOEIC BOT')
        sticker = StickerSendMessage(package_id='2', sticker_id='144')
        message2 = TextSendMessage(text='How are you today?')
        return [image, message1, sticker, message2]

    if arg == 'getID':
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/partnership.png',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/partnership.png'
        )
        message1 = TextSendMessage(text='Please enter your student ID number eg 120123456')

        return [image, message1]

    if arg == 'getTimes':
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png'
        )
        message1 = TextSendMessage(text='What times would you like your question?')
        message2 = TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='Times',
                actions=[
                    PostbackAction(
                        label='early',
                        display_text='9am and 3pm' ,
                        data="['Time', 'early']"
                    ),
                    PostbackAction(
                        label='mid',
                        display_text='10am and 4pm' ,
                        data="['Time', 'mid']"
                    ),
                    PostbackAction(
                        label='late',
                        display_text='11am and 5pm' ,
                        data="['Time', 'late']"
                    )
                ]
            )
        )
        return [image, message1, message2]

    if arg == 'readySet':
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png'
        )
        message1 = TextSendMessage(text='Please try your first question')
        message2 = TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='First Question',
                actions=[
                    PostbackAction(
                        label='A',
                        display_text='A............' ,
                        data="['First', 'A']"
                    ),
                    PostbackAction(
                        label='B',
                        display_text='B............' ,
                        data="['First', 'B']"
                    ),
                    PostbackAction(
                        label='C',
                        display_text='C............' ,
                        data="['First', 'C']"
                    ),
                    PostbackAction(
                        label='D',
                        display_text='D............' ,
                        data="['First', 'C']"
                    )
                ]
            )
        )
        return [image, message1, message2]


    if arg == 'general':
        message = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/faculty.png',
                        action=PostbackAction(
                            label='Faculty',
                            display_text='I would like to know about JUST AFLD teachers...',
                            data="['Faculty', 'None']"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/application.png',
                        action=PostbackAction(
                            label='Application',
                            display_text='How can I apply for JUST AFLD?',
                            data="['Apply', 'None']"
                        )
                    )
                ]
            )
        )
        return message


def follow_check(events):
    newUser = events[0].source.user_id

    if events[0].type == 'follow':
        print('ID follow', newUser)
        profile = line_bot_api.get_profile(newUser)
        print('PROFILE', profile)
        name = profile.display_name

        r.hset(newUser, 'status', 1)
        r.hset(newUser, 'name', name)
        r.hset(newUser, 'passed', json.dumps({}))
        r.hset(newUser, 'failed', json.dumps({}))

        line_bot_api.push_message(newUser, message_list('welcome', name))
        return True

    if events[0].type == 'unfollow':
        print('ID unfollow', newUser)
        r.hset(newUser, 'status', 0)
        return True


@app.route("/callback", methods=['POST'])
def callback():
    print('CALLBACK')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print('SIGNATURE', signature)

    # get request body as text
    body = request.get_data(as_text=True)
    print('BODY', str(body))
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
        follow_check(events)
    except InvalidSignatureError:
        abort(400)

    # handle webhook body
    try:
        print('HANDLER try')
        handler.handle(body, signature)
        print('HANDLER success')
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #message = TextSendMessage(text=event.message.text)
    userID = event.source.user_id
    student = r.hgetall(userID)
    print(student)

    tx = event.message.text

    if int(student['status']) == 1:
        profile = line_bot_api.get_profile(userID)
        name = profile.display_name

        if '120' in event.message.text and len(event.message.text) == 9:
            r.hset(userID, 'studentID', event.message.text)
            r.hset(userID, 'status', 3)
        else:
            message = message_list('getID', event.message.text)

    if int(student['status']) == 2:
        profile = line_bot_api.get_profile(userID)
        name = profile.display_name


        message = message_list('getTimes', name)


    print('EVENT', event)
    line_bot_api.reply_message(event.reply_token, message)



@handler.add(PostbackEvent)
def handle_message(event, destination):
    if isinstance(event.source, SourceUser):
        print('ID', event.source.user_id) # user_id replaces userId

    print('POSTBACK', event.postback.data)
    data = event.postback.data

    if data == 'None':
        pass
        return None
    else:
        userID = event.source.user_id
        student = r.hgetall(userID)

    def send(message):
        line_bot_api.reply_message(event.reply_token, message)

    def push(arg):
        if arg == 1:
            time.sleep(3)
            message = message_list('genConfirm', None)
            line_bot_api.push_message(userID, message)


    data_list = ast.literal_eval(event.postback.data)
    print('DATALIST', data_list)


    if data_list[0] == 'Time':
        r.hset(userID, 'Time', data_list[1])

        message = message_list('readySet', None)
        send(message)

    if data_list[0] == 'First':
        r.hset(userID, 'First', data_list[1])

        message = 'Congrats you have answer your first question'
        send(message)


    return True


@handler.add(FollowEvent)
def handle_follow():
    print('student has joined')

@handler.add(UnfollowEvent)
def handle_unfollow():
    print('student has left')

#If there is no handler for an event, this default handler method is called.
@handler.default()
def default(event):
    print('DEFAULT', event)
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    with open('/', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)




if __name__ == '__main__':
    app.run(debug=DEBUG)

