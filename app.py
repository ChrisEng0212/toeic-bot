from flask import Flask, request, abort, render_template, url_for, flash, redirect, jsonify  
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, timedelta
import json
import os
import ast 

try:
    from meta import SQLALCHEMY_DATABASE_URI, SECRET_KEY, DEBUG, channel_access_token, channel_secret

except:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']    
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message_category = 'info'

# Channel Access Token
line_bot_api = LineBotApi(channel_access_token)
# Channel Secret
handler = WebhookHandler(channel_secret)

parser = WebhookParser(channel_secret)


@login_manager.user_loader
def load_user(user_id):
    return None

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True) 
    username =  db.Column(db.String(20), unique=True, nullable=False)    
    

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    line = db.Column(db.String)
    name = db.Column(db.String)
    highschool = db.Column(db.String)
    number = db.Column(db.String)
    dept = db.Column(db.String)
    questions = db.Column(db.String)    

class Recruits(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    line = db.Column(db.String)
    name = db.Column(db.String)
    highschool = db.Column(db.String)
    ## how did you hear about us?
    number = db.Column(db.String)
    dept = db.Column(db.String)
    questions = db.Column(db.String)
    status = db.Column(db.String)

class MyModelView(ModelView):
    def is_accessible(self):
        if DEBUG == True:
            return True
        else:
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Students, db.session))
admin.add_view(MyModelView(Recruits, db.session))
    

@app.route("/login/<string:pw>", methods=['GET','POST'])
def login(pw):
    print('LOGIN')

    if pw == 'pw':
        user = User.query.filter_by(username='Admin').first()
        print(user.username)
        login_user(user)
        print(user, 'loggedin')
        return redirect (url_for('data')) 
    else:
        return 'Cannot login'

''' UI pages ''' 
  
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/data')
@login_required
def data():
    return 'Data'



''' Line Bot Actions '''

@app.route('/text/<string:tx>')
def text(tx):
    try:
        line_bot_api.multicast(['U2dc560609e55883a4d869c88c0d912e7'], TextSendMessage(text=tx))
        # max 150 recipients
    except LineBotApiError as e:
        abort(400)
    return tx


def message_list(arg, info):

    if arg == "welcome":
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG'
        )
        sticker = StickerSendMessage(package_id='2', sticker_id='144')  
        message1 = TextSendMessage(text='Welcome to JinWen Applied Foreign Languages Department!')        
        message2 = TextSendMessage(text='This BOT is here to help with any question you have about the Department or our application process')    
        print('WELCOME MESSAGE')
        message3 = TemplateSendMessage(
            alt_text='Which department?',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo2.PNG',
                title='Which department?',
                text='Jin Wen Applied Foreign Languages has two divsions',
                actions=[
                    PostbackAction(
                        label='English Division',
                        display_text='Got it. Please write your name first',
                        data="['Division', 'Eng']"
                    ),
                    PostbackAction(
                        label= 'Japanese Division',
                        display_text='Got it. Please write your name first',
                        data="['Division', 'Jpn']"
                    ),              
                    PostbackAction(
                        label= 'Another department',
                        display_text='Got it. Please write your name first',
                        data="['Division', 'Other']"
                    )              
                ]
            )
        )  
        return [image, message1, message2, sticker, message3]
    
    if arg == 'name':
        print('NAME MESSAGE')
        message = TemplateSendMessage(
            alt_text='Your name',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/human.png',
                title='Please check your name.',
                text='You can write it again if you need to.',
                actions=[
                    PostbackAction(
                        label='My name is ' + info,
                        display_text='It would be great to know which high school you attend?',
                        data="['Name', '" + info + "']"
                    ),
                    PostbackAction(
                        label= 'write again',
                        display_text='No problem, try again. 1) What is your name?',
                        data='None'
                    )              
                ]
            )
        )
        print('MESSAGE', message)
        return message
        
    
    if arg == 'high': 
        print('HIGH MESSAGE')
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/partnership.png',
                title='Highschool',
                text='Please check',
                actions=[
                    PostbackAction(
                        label='Highschool: ' + info,
                        display_text='Could we have your phone number for contacting?',
                        data="['High', '" + info + "']"
                    ),
                    PostbackAction(
                        label= 'write again',
                        display_text='Opps, okay, try again. 2) Which highschool do you go to?',
                        data='None'
                    )              
                ]
            )
        )
        print('MESSAGE', message)
        return message
        
    if arg == 'num': 
        print('NUMBER MESSAGE')
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/phone.png',
                title='Phone Number ',
                text='Please check',
                actions=[
                        PostbackAction(
                            label='My number is ' + info,
                            display_text='Thanks, now the BOT can help with some questions you may have', 
                            data="['Num', '" + info + "']"
                        ),
                        PostbackAction(
                            label='Try again',
                            display_text="Sorry, let's try again. 3. What is your number?'", 
                            data='None'
                        ),               
                        PostbackAction(
                            label="No number for me",
                            display_text="No problem, our line BOT is a fine way to get in touch.", 
                            data="['Num', 'None']"
                        )                
                    ]
                )
            )
        return message

    if arg == 'gen': 
        print('GEN MESSAGE')
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/globe.png',
                title='Common Questions',
                text='Choose one',
                actions=[
                        MessageAction(
                            label='The teachers',
                            text='Info coming soon .....',                             
                        ),
                        MessageAction(
                            label='The course',
                            text='Info coming soon .....',                             
                        ),
                        MessageAction(
                            label='Contact a teacher',
                            text='Info coming soon .....',                             
                        ),
                        MessageAction(
                            label='Start an application',
                            text='Info coming soon .....',                             
                        ),
                                      
                    ]
                )
            )
        return message
    



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
        newUser = events[0].source.user_id  
        recruit = Recruits.query.filter_by(line=newUser).first()     
    except InvalidSignatureError:
        abort(400)

    if events[0].type == 'follow':        
        print('ID follow', newUser )        
        if recruit:
            if recruit.status == 'left':
                recruit.status = 'follow'
                db.session.commit()        
        else:            
            newRec = Recruits(line=newUser, status='follow')
            db.session.add(newRec)
            db.session.commit()

        line_bot_api.push_message(newUser, message_list('welcome', None))
        return 'OK'     
    if events[0].type == 'unfollow':
        print('ID unfollow', newUser)
        recruit = Recruits.query.filter_by(line=newUser).first()
        recruit.status = 'left'
        db.session.commit()

    
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
    recruit = Recruits.query.filter_by(line=userID).first()

    if recruit.name == None:
        name = event.message.text
        message = message_list('name', name) # get template to check 
    elif recruit.highschool == None:
        high = event.message.text
        message = message_list('high', high)
    elif recruit.number == None:
        number = event.message.text
        message = message_list('num', num)
    else:
        message = message_list('gen', None)
    
    
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
        recruit = Recruits.query.filter_by(line=userID).first() 

    
    data_list = ast.literal_eval(event.postback.data)
    print('DATALIST', data_list)
    if data_list[0] == 'Division':
        recruit.dept = data_list[1]
    if data_list[0] == 'Name':
        recruit.name = data_list[1]
    if data_list[0] == 'High':
        recruit.high = data_list[1]
    if data_list[0] == 'Num':
        recruit.number = data_list[1]

    db.session.commit()     

    #profile = line_bot_api.get_profile(user_id)
    #print(profile)


    

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




if __name__ == '__main__': 
    app.run(debug=True)

