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
line_bot_api = LineBotApi('1654394560')
# Channel Secret
handler = WebhookHandler('6c1237cad81c1ba197e04f6d179e906e')

@app.route('/')
def hello_world():
    return 'Hello, World!'



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    print('callback')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print(signature)
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    print(message)
    line_bot_api.reply_message(event.reply_token, message)
    
import os
if __name__ == '__main__': 
    app.run(debug=True)
