from flask import Flask, request, abort, render_template, url_for, flash, redirect, jsonify  
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from datetime import datetime, timedelta
import json
import os

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

class MyModelView(ModelView):
    def is_accessible(self):
        if DEBUG == True:
            return True
        else:
            return True
        
 
admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Students, db.session))
    

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
        print('event PARSE', events)
        print('event PARSE', type(events))        
        print('event STRING', str(events))
        print('event STRING', events.type)
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


@handler.add(PostbackEvent)
def handle_message(event, destination):
    print('POSTBACK', event.postback.data)   
    
    if isinstance(event.source, SourceUser):
        print('ID', event.source.user_id) # user_id replaces userId
    
    sticker_message = StickerSendMessage(
    package_id='1',
    sticker_id='1'
    )    
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='yoyo!'), sticker_message])
    
    #profile = line_bot_api.get_profile(user_id)
    #print(profile)


@handler.add(FollowEvent)
def handle_follow():  
    print()


@handler.add(UnfollowEvent)
def handle_follow():        
    print('student has left')


#If there is no handler for an event, this default handler method is called.
@handler.default()
def default(event):
    print('DEFAULT', event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):    
    #message = TextSendMessage(text=event.message.text)  
    
    message = TemplateSendMessage(
    alt_text='Buttons template', # shown on computer --> go to mobile for button view    
    template=ButtonsTemplate(
        thumbnail_image_url='https://lms-tester.s3-ap-northeast-1.amazonaws.com/line-bot/download.jpg',
        title='Menu',
        text='Please select',
        actions=[
                PostbackAction(
                    label='postback',
                    display_text='postback text', # text displayed by user after button clicked
                    data='action=buy&itemid=1'
                ),
                MessageAction(
                    label='message',
                    text='message text'
                ),
                URIAction(
                    label='uri',
                    uri='http://example.com/'
                )
            ]
        )
    )
    
    print('EVENT', event)    
    line_bot_api.reply_message(event.reply_token, message)
    


if __name__ == '__main__': 
    app.run(debug=True)

