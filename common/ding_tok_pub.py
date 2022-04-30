import base64
import hashlib
import hmac
import json
import time
from urllib import parse

import requests


class DingTokPub():
    """
    """

    def __init__(self, webhook: str, secret: str):
        timestamp = str(round(time.time() * 1000))
        self.secret = secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        # 以上就是加签的安全配置，其它安全设置，无需配置以上信息

        webhook = webhook
        self.webhook = "{}&timestamp={}&sign={}".format(webhook, timestamp, sign)
        self.session = requests.session()
        self.session.headers = {"Content-Type": "application/json;charset=utf-8"}

    def send_text_msg(self, content: str, at_mobiles: list = [], at_user_ids: list = [],
                      is_at_all: bool = False) -> object:
        """
        :param content: 发送消息的主题内容
        :param atMobiles: 被@人的手机号。
        :param atUserIds: 被@人的用户userid。
        :param isAtAll: @所有人是true，否则为false。
        :return:
        """
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "atMobiles": at_mobiles,
                    'atUserIds': at_user_ids,
                    "isAtAll": is_at_all
                }
            }
            response = self.session.post(self.webhook, data=json.dumps(data))
            if response.status_code == 200:
                return {"status": True, "message": "消息已发送"}
            else:
                return response.text
        except Exception as error:
            result = {"status": False, "message": f"发送消息失败错误堆栈:{error}"}
            return result

    def send_markdown_msg(self, content: str, title: str, at_mobiles: list = [], at_user_ids: list = [],
                          is_at_all: bool = False) -> object:
        """
        :param content: Markdown格式的消息内容。
        :param title: 主题
        :param at_mobiles: 被@人的手机号。
        :param at_user_ids: 被@人的用户userid。
        :param is_at_all: @所有人是true，否则为false。
        :return:
        """
        if is_at_all:
            content = f'{content} \n@all '
        elif at_mobiles:
            content = f'{content} \n@{" @".join(at_mobiles)}'
        elif at_user_ids:
            content = f'{content} \n@{" @".join(at_user_ids)} '
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                },
                "at": {
                    "atMobiles": at_mobiles,
                    'atUserIds': at_user_ids,
                    "isAtAll": is_at_all
                }
            }
            response = self.session.post(self.webhook, data=json.dumps(data))
            if response.status_code == 200:
                return {"status": True, "message": "消息已发送"}
            else:
                return response.text
        except Exception as error:
            result = {"status": False, "message": f"发送消息失败错误堆栈:{error}"}
            return result
