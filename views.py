#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

# import tornado.gen
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen

class EMDataRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient()
        resp = yield http_client.fetch("")
        self.write("over")


class EMMarketCapUpdate(RequestHandler):
    @gen.coroutine
    def get(self):

        from capital_flow.market_cap import save_single_sto
        r = save_single_sto("000001")
        self.write("update over, r:%s"%repr(r))



handlers = [
    (r"/tmp_em", EMDataRequestHandler),
    (r"/emUpdate", EMMarketCapUpdate),
]