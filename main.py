from pyngrok import ngrok

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
from linebot.exceptions import InvalidSignatureError
from linebot import (
    LineBotApi,
    WebhookHandler,
)
from flask import (
    request,
    abort,
    Flask,
)
from constants import (
    CHANNEL_ACCESS_TOKEN,
    CHANNEL_SECRET,
)

from lineBotFunctions import CloudFunctions

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
ngrok_tunnel = ngrok.connect(5000, bind_tls=True)
line_bot_api.set_webhook_endpoint(f"{ngrok_tunnel.public_url}/callback")
functions = CloudFunctions(line_bot_api, ngrok_tunnel.public_url)


def execute_command(event: MessageEvent) -> None:
    text = event.message.text[1:].lower().strip()
    if text == 'y' or text == 'n':
        functions.quick_reply(event)
    elif text.startswith("y@") or text.startswith("n@"):
        functions.reply_overlay(event)
    elif text == "id":
        functions.get_id(event)
    elif text.startswith("auth@"):
        functions.auth(event)
    elif text.startswith("bind@"):
        functions.bind(event)
    elif text == "help":
        functions.help(event)
    elif text.startswith("adduser@"):
        functions.add_user(event)
    elif text.startswith("removeuser@"):
        functions.remove_user(event)
    elif text.startswith("addadmin@"):
        functions.add_admin(event)
    elif text == "list":
        functions.list_users(event)
    elif text == "report":
        functions.generate_report(event)
    elif text == "clear":
        functions.clear_replies(event)
    elif text == "footprint":
        functions.get_newest_footprint(event)
    elif text == "statistics":
        functions.generate_pie_chart(event)


@app.route("/", methods=['GET'])
def home():
    return "Hello World!"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    text = event.message.text.lower().strip()

    if text.startswith("@"):
        execute_command(event)

    if text == '秉寰':
        return_message = '大佬'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=return_message)
        )


if __name__ == '__main__':
    app.run()
