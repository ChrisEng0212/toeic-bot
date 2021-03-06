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

    destination = None
    response = None

    for k in r.keys():
        if r.hget(k, 'name') == 'Chris':
            destination = k

    print('DEST', destination)
    print('TEXT', tx)


    line_bot_api.push_message(destination, TextSendMessage(text=tx))
    #line_bot_api.broadcast(TextSendMessage(text='Hello World!'))
    #line_bot_api.multicast([k], TextSendMessage(text=tx))
    # max 150 recipients
    # what if recipient has blocked or deleted bot??

    return [tx, response]


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
                        label='early: 9am and 3pm',
                        display_text='9am and 3pm' ,
                        data="['Time', 'early']"
                    ),
                    PostbackAction(
                        label='late: 11am and 5pm',
                        display_text='11am and 5pm' ,
                        data="['Time', 'mid']"
                    )
                ]
            )
        )
        print([image, message1, message2])
        return [image, message1, message2]

    if arg == 'readySet1':
        print('READYSET')
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
                    MessageAction(
                        label='message',
                        text='message text'
                    ),
                ]
            )
        )
        return [image, message1, message2]

    answerDict = {
        1: { 'q': '‘Most of’ the large industries ‘in the’ country ‘are’ well organised and structured and are sometimes ‘backed up’ internationally reputable mother companies.',
             'a': 'D'
             'c': { 'A': 'Most of',
                    'B':'in the',
                    'C' : 'are',
                    'D' : 'backed up'
             },
             'e': ["'are sometimes backed up' is using PASSIVE VOICE, so it would need 'by' --> 'are backed up internationally by' ", "most of ____s, 'the country', 'industires are'"
    }


    question  = 1

    if arg == 'readySet':
        message1 = TextSendMessage(text='Please try your first question')
        message2 = TextSendMessage(
                text='Question........',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a2.png'
                            action=PostbackAction(label="answer1", data=json.dumps(['answer', question, 'A']))
                        ),
                        QuickReplyButton(
                            image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a3.png'
                            action=PostbackAction(label="answer2", data=json.dumps(['answer', question, 'B']))
                        ),
                        QuickReplyButton(
                            image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a2.png'
                            action=PostbackAction(label="answer3", data=json.dumps(['answer', question, 'C']))
                        ),
                        QuickReplyButton(
                            image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a3.png'
                            action=PostbackAction(label="answer4", data=json.dumps(['answer', question, 'D']))
                        )
                    ]
                )
            )
        return [message1, message2]

    if arg == 'readySet2':
        message1 = TextSendMessage(text='Please try your first question')
        message2 = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a3.png',
                        action=PostbackAction(
                            label='A',
                            display_text='answer 1',
                            data=json.dumps(['answer', '1', 'A', info])
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a2.png',
                        action=PostbackAction(
                            label='B',
                            display_text='answer 2',
                            data=json.dumps(['answer', 'B', info])
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/toeic-bot/a1.png',
                        action=PostbackAction(
                            label='C',
                            display_text='answer 3',
                            data=json.dumps(['answer', 'C', info])
                        )
                    )
                ]
            )
        )
        return [message1, message2]

    if arg == 'readySet3':
        print('READYSET')
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
                    MessageAction(
                        label='message',
                        text='message text'
                    ),
                ]
            )
        )
        return [image, message1, message2]


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
    profile = line_bot_api.get_profile(userID)
    name = profile.display_name
    print(student)

    tx = event.message.text

    if int(student['status']) == 1:
        if '120' in event.message.text and len(event.message.text) == 9:
            r.hset(userID, 'studentID', event.message.text)
            r.hset(userID, 'status', 2)
        else:
            message = message_list('getID', event.message.text)

    if int(student['status']) == 2:
        print('getTimes')
        message = message_list('getTimes', name)

    if int(student['status']) == 3:
        print('readySet')
        message = message_list('readySet', name)


    print('EVENT', event)
    print('MESSAGE', message)
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
        r.hset(userID, 'status', 3)
        message = message_list('readySet', None)
        send(message)

    if data_list[0] == 'answer':
        question = data_list[1]
        answer = data_list[2]

        correct = False
        ## check if answer is correct

        if correct:
            pDict = json.loads(student['passed'])
            pDict[question] = str(date.today())
            r.hset(userID, 'passed', json.dumps(pDict)
        else:
            fDict = json.loads(student['failed'])
            fDict[question] = [answer, str(date.today())]
            r.hset(userID, 'failed', json.dumps(pDict)

        message = 'Congrats you have answered your first question'
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

