#! /usr/bin/env python
# coding: utf8
# @Time: 18-02-08
# @Author: yyq

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen

from email.mime.text import MIMEText
from email.header import Header
import smtplib
from config import CFG
from common.log import logger


class EmailHandler(object):
    def __init__(self, *args, **kwargs):
        self.smtp_server = "smtp.126.com"
        self.smtp_port = 465
        self.pwd = ""

    def get_server(self):
        server = smtplib.SMTP_SSL("smtp.126.com", 465)
        server.set_debuglevel(0)
        #server.starttls()
        server.ehlo()
        server.login(CFG.email.sender, CFG.email.pwd)
        return server

    def get_text(self, title="default", msg="no content"):
        text = MIMEText(msg, "html", "utf8")
        text["Subject"] = Header(title, "utf8")
        text["Accept-Language"] = "zh-CN"
        text["Accept-Charset"] = "ISO-8859-1, utf8"
        text["From"] = CFG.email.sender
        text["To"] = CFG.email.rcvr
        return text

    def send(self, title="default", msg="no content"):
        logger.info("EmailHandler, start send")
        msg = self.get_text(title, msg)
        server = self.get_server()
        server.sendmail(CFG.email.sender, [CFG.email.rcvr,], msg.as_string())
        server.quit()
        logger.info("EmailHandler, end send")
        return "email sent"

    def multi_send(self, user_msgs):
        logger.info("EmailHandler, start multi send")
        server = self.get_server()
        for user_email, v in user_msgs.items():
            title, msg = v
            msg = self.get_text(title, msg)
            server.sendmail(CFG.email.sender, [user_email], msg.as_string())

        server.quit()
        logger.info("EmailHandler, end multi send")


class StoRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        codes = self.get_argument("codes")
        print(codes,type(codes))
        #http_client = AsyncHTTPClient()


def send_email(title, msg):
    return EmailHandler().send(title, msg)


def send_multi_emails(user_msgs):
    return EmailHandler().multi_send(user_msgs)

