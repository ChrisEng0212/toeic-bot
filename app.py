from flask import Flask, request, abort

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



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    print('CALLBACK')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print('SIGNATURE', signature)
    # get request body as text
    body = request.get_data(as_text=True)
    print('BODY', body)
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
'''

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    print('EVENT', event)    
    line_bot_api.reply_message(event.reply_token, message)
    
import os
if __name__ == '__main__': 
    app.run(debug=True)
