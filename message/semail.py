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
from config import SrvConfig
from data.log import logger


class EmailHandler(object):
    def __init__(self, *args, **kwargs):
        self.smtp_server = "smtp.126.com"
        self.smtp_port = 465
        self.pwd = ""

    def get_server(self):
        server = smtplib.SMTP_SSL("smtp.126.com", 465)
        server.set_debuglevel(0)
        server.login(SrvConfig.email_sender, SrvConfig.email_pwd)
        return server

    def get_text(self, title="default", msg="no content"):
        text = MIMEText(msg)
        text["Subject"] = Header(title, "utf8")
        text["From"] = SrvConfig.email_sender
        text["To"] = SrvConfig.email_rcvr
        return text

    def send(self, title="default", msg="no content"):
        logger.info("EmailHandler, start send")
        msg = self.get_text(title, msg)
        server = self.get_server()
        server.sendmail(SrvConfig.email_sender, [SrvConfig.email_rcvr,], msg.as_string())
        server.quit()
        logger.info("EmailHandler, end send")


class StoRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        codes = self.get_argument("codes")
        print(codes,type(codes))
        #http_client = AsyncHTTPClient()

@gen.coroutine
def send_email():
    pass

if __name__ == "__main__":
    h = EmailHandler().send()
