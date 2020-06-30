import base64
import hashlib
import hmac

channel_secret = '...' # Channel secret string
body = '...' # Request body string
hash = hmac.new(channel_secret.encode('utf-8'),
    body.encode('utf-8'), hashlib.sha256).digest()
signature = base64.b64encode(hash)
# Compare X-Line-Signature request header and the signature

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
