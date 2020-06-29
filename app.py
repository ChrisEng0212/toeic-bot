from flask import Flask, request, abort
import json

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

    print (body_json['events'][0]['type']) 

    event = body_json['events'][0]  

    if  event['type'] == 'postback':
        line_bot_api.reply_message(event['replyToken'], 'yoyo!')
        return 'ok'

    
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

'''
event {"message": {
    "id": "100001",
     "text": "Hello, world", "type": "text"},
      "replyToken": "00000000000000000000000000000000",
      "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, 
      "timestamp": 1593265283364, 
      "type": "message"
    }
BODY {
    "events":[
        {
            "type":"message",
            "replyToken":"e6e23f53403b446c98d08d7972683c9a",
            "source":{"userId":"U2dc560609e55883a4dc560609e55883a4d869c88c0d912e7","type":"user"},
            "timestamp":1593266202427,
            "mode":"active",
            "message":{"type":"text","id":"12219700373697","text":"okayon":"Udfd15a8989"}
            }
        ],
            "destination":"Udfd15a898e95c5a9525c1d6dfb1f1e40"}
BODY {
    "events":[
        {
            "type":"postback",
            "replyToken":"8c03f680d3844588b212e5746c3e0aff",
            "source":{"userId":"U2dc560609e55883a4d869c88c0d912e7","type":"user"},
            "timestamp":1593444923886,
            "mode":"active",
            "postback":{"data":"action=buy&itemid=1"}
            }
        ],
            "destination":"Udfd15a898e95c5a9525c1d6dfb1f1e40"}
'''

@handler.add(MessageEvent)
def handle_message(event):
    print('POSTBACK', postback.data)
    line_bot_api.reply_message(event.reply_token, 'yoyo!')


@handler.add(FollowEvent)
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
