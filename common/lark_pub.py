import base64
import hashlib
import hmac
import json
import time
import simplejson
import requests
from django.core.cache import cache


class LarkPub:
    def __init__(
        self,
        webhook: str,
        secret: str,
        app_id: str,
        app_secret: str,
    ):
        self.timestamp = int(time.mktime(time.localtime(time.time())))
        self.secret = secret
        self.app_id = app_id
        self.app_secret = app_secret
        # webhook = webhook
        # self.webhook = "{}&timestamp={}&sign={}".format(webhook, timestamp, sign)
        self.webhook = webhook
        self.session = requests.session()
        self.session.headers = {"Content-Type": "application/json;charset=utf-8"}

    def gen_sign(self, timestamp):
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return sign

    def get_tenant_access_token(self):
        tenant_access_token = cache.get("lark_tenant_access_token")
        if not tenant_access_token:
            tenant_url = (
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            )
            data = {"app_id": self.app_id, "app_secret": self.app_secret}
            response = self.session.post(tenant_url, data=simplejson.dumps(data)).json()
            if response["code"] == 0:
                tenant_access_token = response["tenant_access_token"]
                cache.set("lark_tenant_access_token", tenant_access_token, timeout=7200)
            else:
                raise ValueError("获取app token 失败")
        return tenant_access_token

    def get_batch_get_id(self, mobil_list: list):
        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"

        user_id_list = []
        new_mobil_list = []
        lark_batch_id_dic = (
            cache.get("lark_batch_id_dic") if cache.get("lark_batch_id_dic") else {}
        )
        if lark_batch_id_dic:
            for m in mobil_list:
                if m in lark_batch_id_dic:
                    user_id_list.append(lark_batch_id_dic[m])
                else:
                    new_mobil_list.append(m)
        else:
            new_mobil_list = mobil_list
        if new_mobil_list:
            self.session.headers = {
                "Content-Type": "application/json;charset=utf-8;",
                "Authorization": f"Bearer {self.get_tenant_access_token()}",
            }
            data = {"mobiles": new_mobil_list}
            response = self.session.post(url, data=json.dumps(data)).json()
            if response["code"] == 0:
                for uid in response["data"]["user_list"]:
                    if "user_id" in uid:
                        user_id_list.append(uid["user_id"])
                        lark_batch_id_dic[uid["mobile"]] = uid["user_id"]
                cache.set("lark_batch_id_dic", lark_batch_id_dic)
            else:
                raise ValueError("获取用户id列表错误")
        return user_id_list

    def send_text_msg(
        self, content: str, at_mobiles: list = [], is_at_all: bool = False
    ) -> object:
        """
        :param content: 发送消息的主题内容
        :param at_mobiles: 被@人的手机号。
        :param is_at_all: 被@人的用户userid。
        :return:
        """
        try:
            data = {
                "msg_type": "text",
                "timestamp": self.timestamp,
                "sign": self.gen_sign(self.timestamp),
                "content": {"text": content},
            }
            if is_at_all:
                data["content"]["text"] = content + '\n<at user_id="all">所有人</at>'
            elif at_mobiles:
                batch_id_list = self.get_batch_get_id(at_mobiles)
                at_str = ""
                for id in batch_id_list:
                    at_str = at_str + f'<at user_id="{id}">{id}</at>'
                data["content"]["text"] = content + f"\n{at_str}"
            response = self.session.post(self.webhook, data=json.dumps(data)).json()
            if "StatusCode" in response and response["StatusCode"] == 0:
                return True, "消息已发送"
            else:
                return False, response["msg"]
        except Exception as error:
            return False, f"发送消息失败错误堆栈:{error}"

    def send_markdown_msg(
        self, content: str, title: str, at_mobiles: list = [], is_at_all: bool = False
    ) -> object:
        """
        :param content: Markdown格式的消息内容。
        :param title: 主题
        :param at_mobiles: 被@人的手机号。
        :param is_at_all: @所有人是true，否则为false。
        :return:
        """
        try:
            if is_at_all:
                content += f"\n<at id=all></at>"
            elif at_mobiles:
                batch_id_list = self.get_batch_get_id(at_mobiles)
                at_str = ""
                for id in batch_id_list:
                    at_str = at_str + f'<at id="{id}">{id}</at>'
                content += f"\n{at_str}"

            data = {
                "msg_type": "interactive",
                "timestamp": self.timestamp,
                "sign": self.gen_sign(self.timestamp),
                "card": {
                    "config": {"wide_screen_mode": True, "enable_forward": True},
                    "header": {
                        "title": {"tag": "plain_text", "content": title},
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content,
                        }
                    ],
                },
            }
            response = self.session.post(self.webhook, data=json.dumps(data)).json()
            if "StatusCode" in response and response["StatusCode"] == 0:
                return True, "消息已发送"
            else:
                return False, response["msg"]
        except Exception as error:
            return False, f"发送消息失败错误堆栈:{error}"
