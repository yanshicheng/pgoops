import ast

import simplejson
import configparser
from django.conf import settings


class ConfigUtil(object):
    """处理config配置的类"""

    def __init__(self, file=None):
        """
        :param path:
        """
        self.file = file
        self.cf = self.load_init(self.file)

    def load_init(self, file):
        """
        :return: 加载conf
        """
        cf = configparser.ConfigParser()
        cf.read(file)
        return cf

    def get_sections(self):
        """
        :return: 获取文件所有的sections
        """
        sections = self.cf.sections()
        return sections

    def get_options(self, section):
        """
        :param section: 获取某个section所对应的键
        :return:
        """
        options = self.cf.options(section)
        return options

    def get_items(self, sections):
        """
        :param sections: 获取某个section所对应的键值对
        :return:
        """
        items = self.cf.items(sections)
        return items

    def get_value(self, section, key):
        """
        :param sections:
        :param key:
        :return: 获取某个section某个key所对应的value
        """
        value = self.cf.get(section, key)
        return value

    def get_int_val(self, section, key):
        return self.cf.getint(section, key)

    def get_bool_val(self, section, key):
        return self.cf.getboolean(section, key)

    def get_dic_val(self, section, key):
        return simplejson.loads(self.cf.get(section, key))

    def get_list_val(self, section, key):
        return ast.literal_eval(self.cf.get(section, key))

    def get_default(self, key, type="str"):
        match type:
            case "str":
                return self.cf.get("pgoops", key)
            case "int":
                return self.get_int_val("pgoops", key)
            case "list":
                return self.get_list_val("pgoops", key)
            case "dict":
                return self.get_dic_val("pgoops", key)

    def get_mysql(self, key):
        match key:
            case "port":
                return self.get_int_val("db.mysql", key)
            case "options":
                return self.get_dic_val("db.mysql", key)
            case _:
                return self.cf.get("db.mysql", key)

    def get_redis(self, key):
        return self.cf.get("db.redis", key)

    def get_alert_provider_dingtalk(self) -> dict:
        return {
            "webhook": self.get_value("alert.provider", "dingtalk_webhook"),
            "secret": self.get_value("alert.provider", "dingtalk_secret"),
        }

    def get_alert_provider_lark(self) -> dict:
        return {
            "webhook": self.get_value("alert.provider", "lark_webhook"),
            "secret": self.get_value("alert.provider", "lark_secret"),
            "app_id": self.get_value("alert.provider", "lark_app_id"),
            "app_secret": self.get_value("alert.provider", "lark_app_secret"),
        }

    def get_alert_provider_wechat(self) -> dict:
        return {"webhook": self.get_value("alert.provider", "wechat_webhook")}

    def get_alert_provider_email(self) -> dict:
        return {
            "host": self.get_value("alert.provider", "email_smtp_host"),
            "port": self.get_value("alert.provider", "email_smtp_port"),
            "msg_from": self.get_value("alert.provider", "email_msg_from"),
            "secret": self.get_value("alert.provider", "email_secret"),
            "title": self.get_value("alert.provider", "email_title"),
            "domain_name": self.get_value("alert.provider", "email_domain_name"),
        }

    def set_val(self, section, key, val):
        self.cf.set(section, key, val)
        self.save_cf()

    def save_cf(self):
        with open(self.file, "w") as f:
            self.cf.write(f)

    def get_options_dic(self, section):
        if section == "alert.provider":
            al_dic = dict(self.cf.items(section, True))
            for k, v in al_dic.items():
                match k:
                    case "dingtalk_webhook" | "wechat_webhook":
                        r = v.split("=")
                        al_dic[k] = f'{r[0]}={"*" * len(r[1])}'
                    case "lark_webhook":
                        r = v.rsplit("/", 1)
                        al_dic[k] = f'{r[0]}/{"*" * len(r[1])}'
                    case "dingtalk_secret" | "email_secret" | "lark_app_secret" | "lark_app_id" | "lark_secret":
                        al_dic[k] = f'{"*" * len(v)}'
            return al_dic
        else:
            return dict(self.cf.items(section, True))


file = settings.BASE_DIR.joinpath("config", "pgoops.ini")
ConfigDispose = ConfigUtil(file)
