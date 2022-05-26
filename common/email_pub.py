import datetime
import smtplib
from email.mime.text import MIMEText


class EmailPub:
    def __init__(
        self, host, port, msg_from, secret, title="pgoops", domain_name="www.pgoops.com"
    ):
        """
        :param host: SMTP 地址
        :param port: SMTP 号
        :param msg_from: 邮件地址 xx@163.com
        :param secret: 密钥
        :param title: 系统名称
        :param domain_name: 系统域名
        """
        self.data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.msg_from = msg_from
        self.title = title
        self.domain_name = domain_name
        self.smtp_s = smtplib.SMTP_SSL(host=host, port=port)
        self.smtp_s.login(user=msg_from, password=secret)

    def send_html_msg(self, content: str, to_user: list, subject: str):
        """
        发送文本邮件
        :param to_user: 对方邮箱
        :param content: 邮件正文, html 竖向表格 格式 <tr><td>title</td> <td>value</td> </tr> 为一行
        :param subject: 邮件主题
        :return:
        """
        contents = self.__html_template(content)
        msg = MIMEText(contents, _subtype="html", _charset="utf8")
        from email.header import Header

        to_users = ",".join(to_user)
        msg["From"] = Header(self.title, "utf-8")
        msg["To"] = Header(to_users, "utf-8")
        msg["subject"] = Header(subject, "utf-8")
        self.smtp_s.send_message(msg, from_addr=self.msg_from, to_addrs=to_user)

    def __html_template(self, content: str) -> str:
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>pgoops通知邮件</title>
</head>
<body>
<div>
    <includetail>
        <div style="font:Verdana normal 14px;color:#000;">
            <div style="position:relative;">

                <div class="eml-w eml-w-sys-layout">
                    <a href="http://{self.domain_name}" style="color: #2b2b2b">
                        <div>
                            <p style="font-size:15px;word-break:break-all;padding: 23px 32px;margin:0;background-color: #337ae8;border-radius: 10px 10px 0 0;font-size:16px">
                                {self.title}平台
                            </p>
                        </div>
                    </a>
                    <div style="font-size: 0px;">
                        <div class="eml-w-sys-line">
                            <div class="eml-w-sys-line-left"></div>
                            <div class="eml-w-sys-line-right"></div>
                        </div>
                        <!--       Logo                 -->
                        <!--                        <div class="eml-w-sys-logo">-->
                        <!--                            <img class="eml-w-sys-logo" src="http://www.pgoops.com/assets/img/superops.9a5b3f97.png"-->
                        <!--                                 style="width: 34px; height: 34px;" onerror="">-->
                        <!--                        </div>-->
                    </div>
                    <div class="gen-item">
                        <div class="eml-w-item-block"
                             style="padding: 0px;margin-left: 10px;font-size: 22px;color: #36649d;font-weight: bold">
                            <div class="eml-w-title-level1">详细信息如下：</div>
                        </div>
                    </div>
                    <div style="border: #36649d 1px dashed;margin: 20px;padding: 20px">
                        <table style=" width: 100%">
                            {content}
                        </table>
                    </div>
                    <div class="eml-w-sys-content">
                    </div>
                    <td>
                        <div style="margin: 40px"><p style="font-size: 16px"><a
                                href="http://{self.domain_name}">{self.title}管理团队</a></p>
                            <p style="color:red;font-size: 14px ">（这是一封自动发送的邮件，请勿回复。）</p></div>
                    </td>
                    <td>
                        <div align="right" style="margin: 40px;border-top: solid 1px gray" id="bottomTime"><p
                                style="margin-right: 20px"><a href="http://{self.domain_name}">{self.title}自动化运维平台</a>
                        </p> <label
                                style="margin-right: 20px">{self.data_time}</label></div>
                    </td>
                    <div class="eml-w-sys-footer" style="margin: 0 auto; text-align: center"><a
                            href="http://{self.domain_name}">{self.domain_name}</a></div>
                </div>
            </div>
        </div>
    </includetail>
</div>
</body>
</html>
        """
