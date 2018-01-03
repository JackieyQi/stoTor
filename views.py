#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

# import tornado.gen
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen

class EMDataRequestHandler(RequestHandler):
    @gen.cotoutine
    def get(self):
        http_client = AsyncHTTPClient()
        resp = yield http_client.fetch("")
        self.write("over")


handlers = [
    (r"/em", EMDataRequestHandler),
]