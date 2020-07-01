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

    if arg == 'alert': 
        message = TextSendMessage(text='Sorry this answer is too long, please make it shorter (<10)') 
        return message

    if arg == "welcome":
        image = ImageSendMessage(
            original_content_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG',
            preview_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo1.PNG'
        )        
        message1 = TextSendMessage(text='Welcome to JinWen Applied Foreign Languages Department!')  
        sticker = StickerSendMessage(package_id='2', sticker_id='144')  
        message2 = TextSendMessage(text='How are you today?')  
        return [image, message1, sticker, message2]

    if arg == 'start':
        message1 = TextSendMessage(text='This BOT is here to help with any question you have about the Department or our application process')   
        message2 = TextSendMessage(text='First we need some simple details')  
        message3 = TemplateSendMessage(
            alt_text='What is your name?',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo2.PNG',
                title='What is your name?',
                text='Should we use your line name?',
                actions=[
                    PostbackAction(
                        label=info,
                        display_text='Thanks, got it. Next, please write your highschool...',
                        data="['Name', '" + info + "']"
                    ),
                    PostbackAction(
                        label= 'Write name',
                        text='Okay. Please write your name....',
                        data="['Name', '159']"
                    ),              
                                
                ]
            )
        )  
        return [message1, message2, message3]

    
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
                        display_text='Please tell us which high school you attend?',
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
                        label='School: ' + info,
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
                            label='Phone: ' + info,
                            display_text='Thanks, now which department are you interested in?', 
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

    if arg == "dept":         
        print('WELCOME MESSAGE')
        message = TemplateSendMessage(
            alt_text='Which department?',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/logo2.PNG',
                title='Which department?',
                text='Jin Wen Applied Foreign Languages has two divsions',
                actions=[
                    PostbackAction(
                        label='English Division',
                        display_text='Got it. Now the bot can help you with your questions',
                        data="['Division', 'Eng']"
                    ),
                    PostbackAction(
                        label= 'Japanese Division',
                        display_text='Got it. Now the bot can help you with your questions',
                        data="['Division', 'Jpn']"
                    ),              
                    PostbackAction(
                        label= 'Another department',
                        display_text='Got it. Now the bot can help you with your questions',
                        data="['Division', 'Other']"
                    )              
                ]
            )
        )  
        return message

    if arg == 'check': 
        print('CHECK MESSAGE')
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url= 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/globe.png',
                title='Thank you for getting in touch',
                text='Name:  Highschool:...',
                actions=[
                        PostbackAction(
                            label="All good :)",
                            display_text="Nice, now lets think more about your future studies", 
                            data="Done"
                        ),
                        PostbackAction(
                            label="Start again",
                            display_text="No problem, from the top! 1) What is your name?", 
                            data="Restart"
                        ),
                        
                                      
                    ]
                )
            )
        return message

    if arg == 'gen1': 
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

    if arg == 'gen':
        message = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
                        action=PostbackAction(
                            label='Faculty',
                            display_text='Info coming soon...',
                            data="['None', 'None']"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
                        action=PostbackAction(
                            label='Application',
                            display_text='Info coming soon...',
                            data="['None', 'None']"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
                        action=PostbackAction(
                            label='Courses',
                            display_text='Info coming soon...',
                            data="['None', 'None']"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
                        action=PostbackAction(
                            label='Contact',
                            display_text='Info coming soon...',
                            data="['None', 'None']"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
                        action=PostbackAction(
                            label='Why study languages?',
                            display_text='Info coming soon...',
                            data="['None', 'None']"
                        )
                    )
                    
                ]
            )
        )
        return message
    
    

    
def rich_menu(userID):        
    rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1600),
    selected=False,
    name="Nice richmenu",
    chat_bar_text="Tap here",
    areas=[
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=800),
        action=URIAction(label='Go to line.me', uri='https://line.me'))  
        ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print('RMID ', rich_menu_id)

    with open('banner.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)
    
    'https://medium.com/enjoy-life-enjoy-coding/%E4%BD%BF%E7%94%A8-python-%E7%82%BA-line-bot-%E5%BB%BA%E7%AB%8B%E7%8D%A8%E4%B8%80%E7%84%A1%E4%BA%8C%E7%9A%84%E5%9C%96%E6%96%87%E9%81%B8%E5%96%AE-rich-menus-7a5f7f40bd1'

    line_bot_api.link_rich_menu_to_user(userID, rich_menu_id)   


def follow_check(events):
    newUser = events[0].source.user_id 

    if events[0].type == 'follow':        
        print('ID follow', newUser)  
        newRec = Recruits(line=newUser, status='follow')
        db.session.add(newRec)
        db.session.commit()
       
        try:
            line_bot_api.unlink_rich_menu_from_user(newUser)    
        except: 
            pass 
        line_bot_api.push_message(newUser, message_list('welcome', None))
        return 'OK'   

    if events[0].type == 'unfollow':
        print('ID unfollow', newUser)
        recruit = Recruits.query.filter_by(line=newUser).first()
        recruit.status = 'left'
        recruit.line = '0000__' + recruit.line
        db.session.commit()



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
    recruit = Recruits.query.filter_by(line=userID).first()

    tx = event.message.text

    if recruit.name == None:
        profile = line_bot_api.get_profile(userID)
        name = profile.display_name
        message = message_list('start', name) # get template to check         
    elif recruit.name == '159':
        if len(tx) < 11: 
            name = event.message.text
            message = message_list('name', name)
        else:
            message = message_list('alert', None)        
        
    elif recruit.highschool == None:
        if len(tx) < 11: 
            high = event.message.text
            message = message_list('high', high)
        else:
            message = message_list('alert', None)
    elif recruit.number == None:
        if len(tx) < 11: 
            number = event.message.text
            message = message_list('num', number)
        else:
            message = message_list('alert', None)
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
    
    data_list = ast.literal_eval(event.postback.data)
    print('DATALIST', data_list)
    if data_list[0] == 'Division':
        recruit.dept = data_list[1]  
        message = message_list('gen', None)
        line_bot_api.reply_message(event.reply_token, message)
        rich_menu(userID)      
    if data_list[0] == 'Name':
        recruit.name = data_list[1]       
    if data_list[0] == 'High':
        recruit.highschool = data_list[1]
    if data_list[0] == 'Num':        
        recruit.number = data_list[1]
        message = message_list('dept', None)
        line_bot_api.reply_message(event.reply_token, message)
        


    db.session.commit()   
    return 'OK'  

   

    

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

