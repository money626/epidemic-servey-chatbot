from __future__ import annotations

from errors import NoSuchUserError
from typing import Callable, Any
from constants import (
    COMMAND_NOT_AVAILABLE_MESSAGE,
    NAME,
    OVERLAP,
    PASSWORD,
    PERMISSION_DENIED_MESSAGE,
    USER_NOT_BOUND_MESSAGE,
)
from functools import wraps
from linebot.api import LineBotApi
from linebot.models.events import MessageEvent
from linebot.models.send_messages import (
    ImageSendMessage,
    TextSendMessage,
)
from firebase import CloudFirebase

import requests
from bs4 import BeautifulSoup


class Commands(object):
    @staticmethod
    def has_permission(func: Callable[[CloudFunctions, MessageEvent, Any, Any], None]):
        @wraps(func)
        def wrapper(cls: CloudFunctions, event: MessageEvent, *args, **kwargs):
            user_id = event.source.user_id
            if not cls.db.is_admin(user_id):
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=PERMISSION_DENIED_MESSAGE)
                )
                return None
            return func(cls, event, *args, **kwargs)

        return wrapper

    @staticmethod
    def personal_only(func: Callable[[CloudFunctions, MessageEvent, Any, Any], None]):
        @wraps(func)
        def wrapper(cls: CloudFunctions, event: MessageEvent, *args, **kwargs):
            if event.source.type != 'user':
                return None
            return func(cls, event, *args, **kwargs)

        return wrapper

    @staticmethod
    def group_only(func: Callable[[CloudFunctions, MessageEvent, Any, Any], None]):
        @wraps(func)
        def wrapper(cls: CloudFunctions, event: MessageEvent, *args, **kwargs):
            if event.source.type == 'user':
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=COMMAND_NOT_AVAILABLE_MESSAGE)
                )
                return None
            return func(cls, event, *args, **kwargs)

        return wrapper

    @staticmethod
    def bound_only(func: Callable[[CloudFunctions, MessageEvent, Any, Any], None]):
        @wraps(func)
        def wrapper(cls: CloudFunctions, event: MessageEvent, *args, **kwargs):
            user_id = event.source.user_id
            if not cls.db.is_bound(user_id):
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=USER_NOT_BOUND_MESSAGE)
                )
                return None
            return func(cls, event, *args, **kwargs)

        return wrapper


class CloudFunctions(object):
    def __init__(self, line_bot_api: LineBotApi, base_url: str):
        self.line_bot_api = line_bot_api
        self.db = CloudFirebase()
        self.BASE_URL = base_url

    @Commands.has_permission
    def add_user(self, event: MessageEvent):
        name = event.message.text[9:]
        self.db.add_user(name)
        reply_message = f"?????????????????????{name}"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def remove_user(self, event: MessageEvent):
        name = event.message.text[12:]
        self.db.remove_user(name)
        reply_message = f"?????????????????????{name}"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def add_admin(self, event: MessageEvent):
        self.db.add_admin(event.message.text[10:])
        reply_message = "??????????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def list_users(self, event: MessageEvent):
        users = "\n".join(self.db.get_user_name_list())
        reply_message = f"?????????????????????????????????????????????????????????????????????????????????~\n{users}"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def generate_report(self, event: MessageEvent):
        data = self.db.get_user_dict().values()

        overlap_count = len([1 for i in data if i.get(OVERLAP) is True])
        no_overlap_count = len([1 for i in data if i.get(OVERLAP) is False])
        not_replied = [i[NAME] for i in data if i.get(OVERLAP) is None]
        not_replied_count = len(not_replied)
        not_replied = ",".join(not_replied)

        msgs = [
            f'????????????{no_overlap_count}???',
            f'????????????{overlap_count}???',
            '',
            '-------------------------',
            f'????????????{not_replied_count}???',
            f'{not_replied}',
            '-------------------------',
        ]
        reply_message = "\n".join(msgs)
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def clear_replies(self, event: MessageEvent):
        self.db.clear_replies()
        reply_message = "?????????????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    def reply_overlay(self, event: MessageEvent):
        overlap = event.message.text[1] == 'y'
        name = event.message.text[3:]
        self.db.add_reply(name, overlap)
        if overlap:
            reply_message = f"?????????{name}????????????????????????????????????????????????????????????"
        else:
            reply_message = f"?????????{name}?????????????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    def help(self, event: MessageEvent):
        msgs = [
            "????????????????????????",
            "@help",
            "@y@name or @n@name: ????????????,???????????????",
            "@bind@name: ??????line????????????????????? (????????????????????????)"
            "@y or @n ??????????????????,??????????????? (???????????????)"
            "@id: ???????????????line id (?????????????????????)",
            "--------------------------------------",
            "????????????????????????",
            "@addUser@name: ?????????????????????",
            "@removeUser@name: ?????????????????????",
            "@addAdmin@userID: ???????????????",
            "@list: ???????????????????????????",
            "@report: ??????????????????",
            "@clear: ????????????????????????",
            "@statistics: ???????????????????????????",
            "@footprint: ????????????????????????",
            "--------------------------------------"
        ]
        reply_message = "\n".join(msgs)
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.personal_only
    def auth(self, event: MessageEvent):
        if event.message.text[6:] == PASSWORD:
            self.db.add_admin(event.source.user_id)
            reply_message = "??????????????????"
        else:
            reply_message = "????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.personal_only
    def get_id(self, event: MessageEvent):
        reply_message = event.source.user_id
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.group_only
    def bind(self, event: MessageEvent):
        name = event.message.text[6:]
        user_id = event.source.user_id
        try:
            self.db.bind_user(user_id, name)
            reply_message = f"????????????????????????: {name}"
        except NoSuchUserError:
            reply_message = f"?????????????????????: {name}????????????????????????????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.bound_only
    def quick_reply(self, event: MessageEvent):
        overlap = event.message.text[1].lower() == 'y'
        key = self.db.get_bound_key(event.source.user_id)
        name = self.db.get_name_by_key(key)
        self.db.add_reply_by_key(key, overlap)
        if overlap:
            reply_message = f"?????????{name}????????????????????????????????????????????????????????????"
        else:
            reply_message = f"?????????{name}?????????????????????"
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    @Commands.has_permission
    def get_newest_footprint(self, event: MessageEvent):
        url = "https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ"
        res = requests.post(url, {
            "keyword": "?????????"
        })
        soup = BeautifulSoup(res.text, features="html.parser")
        href = soup.find("div", attrs={
            "class": "content-boxes-v3"
        }).find("a")["href"]
        article_url = f"https://www.cdc.gov.tw{href}"
        article_res = requests.get(article_url)
        article_soup = BeautifulSoup(article_res.text, features="html.parser")
        urls = [
            img['src']
            for img in article_soup.find_all("img")
            if img['src'].startswith('/Uploads/')
        ]
        if len(urls) == 0:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("?????????????????????????????????")
            )
            return
        self.line_bot_api.reply_message(
            event.reply_token,
            [
                ImageSendMessage(
                    original_content_url=f"https://www.cdc.gov.tw{target_url}",
                    preview_image_url=f"https://www.cdc.gov.tw{target_url}"
                ) for target_url in urls
            ]
        )

    @Commands.has_permission
    def generate_pie_chart(self, event: MessageEvent):
        self.db.generate_pie_chart()
        self.line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=f"{self.BASE_URL}/static/statistic.png",
                preview_image_url=f"{self.BASE_URL}/static/statistic.png"
            )
        )
