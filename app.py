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
    channel_access_token = os.environ['CHANNEL_ACCESS']
    channel_secret = os.environ['CHANNEL_SECRET']


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
        user = User.query.filter_by(username='Admin').first()
        print(user.username)
        print(user, 'loggedin')
        return redirect (url_for('data'))
    else:
        return 'Cannot login'

''' UI pages '''

@app.route('/')
def home():
    return render_template('/home.html')

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

    if arg == 'nameSet':
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/partnership.png',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/partnership.png'
        )
        message = TextSendMessage(text='Thanks, got it. Next, please write your highschool...')
        return [image, message]

    if arg == 'deptSet':
        sticker = StickerSendMessage(package_id='2', sticker_id='141')
        message = TextSendMessage(text='Great, all set. Now the BOT can help with any questions you might have about the Department or our Application Process')
        return [sticker, message]

    if arg == 'start2':
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png'
        )
        message3 = TextSendMessage(text='Should we use your LINE name?')
        message4 = TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='Name',
                actions=[
                    PostbackAction(
                        label=info,
                        display_text='NAME SET: ' + info ,
                        data="['Name', '" + info + "']"
                    ),
                    PostbackAction(
                        label= 'Not this',
                        display_text='Name...',
                        data="['Name', '159']"
                    ),
                ]
            )
        )
        return [image, message3, message4]

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

    tx = event.message.text

    if student.status < 2:
        profile = line_bot_api.get_profile(userID)
        name = profile.display_name
        if student.name == None:
            message = message_list('start1', name)
            line_bot_api.push_message(userID, message)
            time.sleep(4)
            message = message_list('start2', name)
        elif student.name == '159':
            if len(tx) < 21:
                name = event.message.text
                message = message_list('nameConfirm', name)
            else:
                message = message_list('alert', None)

    elif student.status < 3:
        if len(tx) < 21:
            high = event.message.text
            message = message_list('highConfirm', high)
        else:
            message = message_list('alert', None)
    elif student.status < 4:
        if len(tx) < 21:
            number = event.message.text
            message = message_list('numConfirm', number)
        else:
            message = message_list('alert', None)
    else:
        message = message_list('general', None)


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

    '''
    if data == 'Done':
        ## send message
        return 'OK'
    if data == 'Restart':
        recruit.delete()
        db.session.commit()
        newRec = Recruits(line=userID, status='follow')
        db.session.add(newRec)
        db.session.commit()
        return 'OK'
    '''

    def send(message):
        line_bot_api.reply_message(event.reply_token, message)

    def push(arg):
        if arg == 1:
            time.sleep(3)
            message = message_list('genConfirm', None)
            line_bot_api.push_message(userID, message)


    data_list = ast.literal_eval(event.postback.data)
    print('DATALIST', data_list)


    if data_list[0] == 'Name':
        if data_list[1] == '159':
            recruit.name = data_list[1]
            message = TextSendMessage(text='Please enter your name...')
            send(message)
        else:
            recruit.name = data_list[1]
            recruit.status = 2
            message = message_list('nameSet', None)
            send(message)

    if data_list[0] == 'High':
        if data_list[1] == None:
            message = TextSendMessage(text='Please enter your highschool...')
            send(message)
        else:
            recruit.highschool = data_list[1]
            recruit.status = 3
            message = message_list('highSet', None)
            send(message)
    if data_list[0] == 'Num':
        if data_list[1] == None:
            message = TextSendMessage(text='Please enter your phone number...')
            send(message)
        else:
            recruit.number = data_list[1]
            recruit.status = 4
            message = message_list('numSet', None)
            send(message)
    if data_list[0] == 'Division':
        recruit.dept = data_list[1]
        recruit.status = 5
        message = message_list('deptSet', None)
        line_bot_api.push_message(userID, message)
        time.sleep(2)
        message = message_list('general', None)
        send(message)
        #rich_menu(userID)


    if data_list[0] == 'Faculty':
        recruit.set1 = data_list[0]
        message = TextSendMessage(text='Faculty info coming soon...')
        send(message)
        push(1)
    if data_list[0] == 'Courses':
        recruit.set2 = data_list[0]
        message = TextSendMessage(text='Courses info coming soon...')
        send(message)
        push(1)
    if data_list[0] == 'Contact':
        recruit.set3 = data_list[0]
        message = TextSendMessage(text='Here is a list of professors you can add to your LINE....')
        send(message)
        push(1)
    if data_list[0] == 'Why':
        recruit.set4 = data_list[0]
        message = TextSendMessage(text='Why study langauges? Why study at university? Answers coming soon....')
        send(message)
        push(1)
    if data_list[0] == 'Apply':
        recruit.set5 = data_list[0]
        message = TextSendMessage(text='Our application process is very easy. First...')
        send(message)
        push(1)

    if data_list[0] == 'Gen':
        if data_list[1] =='Yes':
            message = message_list('general', None)
            send(message)
        else:
            m1 = TextSendMessage(text='Great, thank you for paying an interest in our department.')
            m2 = TextSendMessage(text='JUST-BOT will send some useful information in the future')
            m3 = TextSendMessage(text='Just say "Hi" to get more information')
            sticker = StickerSendMessage(package_id='2', sticker_id='159')

            send([m1, m2, sticker, m3])

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

