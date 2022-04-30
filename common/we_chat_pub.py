import json

import requests


class WeChatPub:
    def __init__(self, webhook: str):
        self.webhook = webhook
        self.session = requests.session()
        self.session.headers = {"Content-Type": "application/json;charset=utf-8"}

    def send_text_msg(self, content: str, mentioned_mobile_list: list = []):
        """
        :param content: text 格式消息
        :param mentioned_mobile_list: 被@人的手机号。列表格式，
        :return:
        """
        try:
            data = {
                "msgtype": "text",

                "text": {
                    "content": content,
                    "mentioned_mobile_list": mentioned_mobile_list
                },
            }
            response = self.session.post(self.webhook, data=json.dumps(data))
            if response.status_code == 200:
                return {"status": True, "message": "消息已发送"}
            else:
                return response.text
        except Exception as error:
            result = {"status": False, "message": f"发送消息失败错误堆栈:{error}"}
            return result

    def send_markdown_msg(self, content: str, mentioned_mobile_list: list = []):
        """
        :param content: markdown 格式消息
        :param mentioned_mobile_list: 被@人的手机号。列表格式，暂时不支持等待官方支持
        :return:
        """
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content,
                    "mentioned_mobile_list": mentioned_mobile_list
                },
            }
            response = self.session.post(self.webhook, data=json.dumps(data))
            if response.status_code == 200:
                return {"status": True, "message": "消息已发送"}
            else:
                return response.text
        except Exception as error:
            result = {"status": False, "message": f"发送消息失败错误堆栈:{error}"}
            return result
