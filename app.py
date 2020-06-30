from flask import Flask, request, abort
import json
import abc


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('HzvSBrRQ11nxA+2sex/gtMWHL0DjzhJZy6VOK/i0aFh1836BK0ifbYJYarNehZgD6xFwlrSU6E9b2f00VaAHyVYOweaLpJLYWuHFTMljLBuszbcEqPEQzaVr/yWQ3Y1tetD6goR3u6FHCNDjDeFzwgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('6c1237cad81c1ba197e04f6d179e906e')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/text/<string:tx>')
def text(tx):
    try:
        line_bot_api.multicast(['U2dc560609e55883a4d869c88c0d912e7'], TextSendMessage(text=tx))
        # max 150 recipients
    except LineBotApiError as e:
        abort(400)
    return tx



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    print('CALLBACK')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print('SIGNATURE', signature)

    body_json = json.loads(request.get_data())

        
    # get request body as text
    body = request.get_data(as_text=True)
    print('BODY', str(body))
    app.logger.info("Request body: " + body)
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
    print('RepTOK', event.reply_token)
    print('ID', event.source)  
    print(SourceUser()) 
    

    
    sticker_message = StickerSendMessage(
    package_id='1',
    sticker_id='1'
    )    
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='yoyo!'), sticker_message])
    
    #profile = line_bot_api.get_profile(user_id)
    #print(profile)



@handler.add(FollowEvent)
def handle_follow():    
    line_bot_api.reply_message(event.reply_token, 'welcome')



@handler.add(UnfollowEvent)
def handle_follow():        
    line_bot_api.reply_message(event.reply_token, 'welcome')



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

