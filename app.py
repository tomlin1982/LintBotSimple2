# 運行以下程式需安裝模組: line-bot-sdk, flask, pyquery
# 安裝方式，輸入指令: pip install 模組名稱


#開發
#1. 電腦安裝需要的模組
#   pip install -r requments.txt
#2. 啟動 ngrok 測試網址(通道)
#3. 啟動應用程式 python app.py
#4. 將測試網址更新Line Webhook


# 引入flask模組
from flask import Flask, request, abort
# 引入linebot相關模組
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

# 如需增加其他處理器請參閱以下網址的 Message objects 章節
# https://github.com/line/line-bot-sdk-python
from linebot.models import (
    MessageEvent,
    TextMessage,
    StickerMessage,
    TextSendMessage,
    StickerSendMessage,
    LocationSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackAction,
    MessageAction,
    URIAction,
    CarouselTemplate,
    CarouselColumn
)

from modules.reply import faq, menu
from modules.currency import get_exchange_table

table = get_exchange_table()


# 定義應用程式是一個Flask類別產生的實例
app = Flask(__name__)

# LINE的Webhook為了辨識開發者身份所需的資料
# 相關訊息進入網址(https://developers.line.me/console/)
CHANNEL_ACCESS_TOKEN = 'Hd7CQc1zcysF1pVgCbkHQDuRy/squKGYYmu+dWl5vMepK6GPruMCnl/9PJWnFAyhVAe8OLa8EAuuhZw0a2URXykyf3jf8eo6UgfNMLmesTCdo+p/r08zWBMSIzv1gtH1qbu55OOBr/zqEG0c/F1UbwdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = 'c80bf935231f8e451bce7ea5d3c90c5b'

# ********* 以下為 X-LINE-SIGNATURE 驗證程序 *********
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
@app.route("/", methods=['POST'])
def callback():
    # 當LINE發送訊息給機器人時，從header取得 X-Line-Signature
    # X-Line-Signature 用於驗證頻道是否合法
    signature = request.headers['X-Line-Signature']

    # 將取得到的body內容轉換為文字處理
    body = request.get_data(as_text=True)
    print("[app.route]訊息進入X-Line-Signature驗證程序")
    # print(body)

    # 一但驗證合法後，將body內容傳至handler
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# ********* 以上為 X-LINE-SIGNATURE 驗證程序 *********


# 文字訊息傳入時的處理器
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 當有文字訊息傳入時
    # event.message.text : 使用者輸入的訊息內容
    print('*'*30)
    print('[使用者傳入文字訊息]')
    print(str(event))
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    # 取得使用者說的文字
    user_msg = event.message.text
    print(f"{profile.display_name}剛才傳「{user_msg}」訊息給機器人")
    # 準備要回傳的文字訊息
    reply = menu
    if user_msg in faq:
        reply = faq[user_msg]
    elif user_msg in table:
        bid = table[user_msg]['bid']
        offer = table[user_msg]['offer']
        report = f"{user_msg}\n 買價:{bid} 賣價:{offer}"
        reply = TextSendMessage(text=report)

    # 回傳訊息
    # 若需要回覆多筆訊息可使用
    # line_bot_api.reply_message(token, [Object, Object, ...])
    line_bot_api.reply_message(
        event.reply_token,
        reply)


# 貼圖訊息傳入時的處理器 
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # 當有貼圖訊息傳入時
    print('*'*30)
    print('[使用者傳入貼圖訊息]')
    print(str(event))

    # 準備要回傳的貼圖訊息
    # HINT: 機器人可用的貼圖 https://devdocs.line.me/files/sticker_list.pdf
    reply = StickerSendMessage(package_id='2', sticker_id='149')

    # 回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        reply)


import os
if __name__ == "__main__":
    print('[伺服器開始運行]')
    # 取得遠端環境使用的連接端口，若是在本機端測試則預設開啟於port=5500
    # port = int(os.environ.get('PORT', 5050))
    port = int(os.environ.get('PORT', 5050))
    # 使app開始在此連接端口上運行
    print(f'[Flask運行於連接端口:{port}]')
    # 本機測試使用127.0.0.1, debug=True
    # Heroku部署使用 0.0.0.0
    #app.run(host='127.0.0.1', port=port, debug=True)
    app.run(host='0.0.0.0', port=port, debug=True)