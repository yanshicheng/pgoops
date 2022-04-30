from common.config_dispose import ConfigDispose
from common.ding_tok_pub import DingTokPub
from common.we_chat_pub import WeChatPub
from common.email_pub import EmailPub


class MessageProvider:
    def __init__(self, instance):
        self.instance = instance
        self.is_at_all = self.instance.is_all
        self.title = 'pgoops平台告警系统'

    def get_user_list(self):
        if self.instance.is_at:
            return self.at_to_user()
        else:
            return []

    def at_to_user(self):
        raise NotImplementedError(f'{self.__class__.__name__}, There is no implementation  send_to_group  methods')

    def send_to_group(self):
        raise NotImplementedError(f'{self.__class__.__name__}, There is no implementation  send_to_group  methods')

    def markdown_message(self):
        if getattr(self.__class__, '__name__') == 'DingTokProvider':
            return self.instance.get_markdown_message(sign='\n\n')
        else:
            return self.instance.get_markdown_message()

    def test_message(self):
        if getattr(self.__class__, '__name__') == 'DingTokProvider':
            return self.instance.get_text_message(sign='\n')
        else:
            return self.instance.get_text_message()

    def html_message(self):
        return self.instance.get_html_message()


class DingTokProvider(MessageProvider):
    def __init__(self, instance):
        super(DingTokProvider, self).__init__(instance)
        self.provider = DingTokPub(**ConfigDispose.get_alert_provider_dingtop())

    def send_text_msg(self):

        text_message = self.test_message()
        self.provider.send_text_msg(content=text_message, at_mobiles=self.get_user_list(),
                                    is_at_all=self.is_at_all)

    def send_markdown_msg(self):
        markdown_message = self.markdown_message()
        self.provider.send_markdown_msg(content=markdown_message, title=self.title, at_mobiles=self.get_user_list(),
                                        is_at_all=self.is_at_all)

    def at_to_user(self):
        u = []
        if self.instance.is_all:
            u.append('@all')
            return u
        elif self.instance.user:
            u.append(self.instance.user.phone)
            return u
        else:
            return self.instance.level.get_phone_list()


class EmailProvider(MessageProvider):
    def __init__(self, instance):
        super(EmailProvider, self).__init__(instance)
        self.provider = EmailPub(**ConfigDispose.get_alert_provider_email())

    def send_html_msg(self):
        html_message = self.html_message()
        self.provider.send_html_msg(content=html_message, to_user=self.get_user_list(),
                                    subject=self.title)

    def at_to_user(self):
        u = []
        if self.instance.user:
            u.append(self.instance.user.email)
            return u
        else:
            return self.instance.level.get_email_list()


class WeChatProvider(MessageProvider):
    def __init__(self, instance):
        super(WeChatProvider, self).__init__(instance)
        self.provider = WeChatPub(**ConfigDispose.get_alert_provider_wechat())

    def send_text_msg(self):
        text_message = self.test_message()
        self.provider.send_text_msg(content=text_message, mentioned_mobile_list=self.get_user_list(), )

    def send_markdown_msg(self):
        markdown_message = self.markdown_message()
        self.provider.send_markdown_msg(content=markdown_message, mentioned_mobile_list=self.get_user_list())

    def at_to_user(self):
        u = []
        if self.instance.is_all:
            u.append('@all')
            return u
        elif self.instance.user:
            u.append(self.instance.user.phone)
            return u
        else:
            return self.instance.level.get_phone_list()
