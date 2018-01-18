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
        self.write("update over, r:%s \n" % repr(r))


class CronAddStoCode(RequestHandler):
    def get(self):
        from data.sto_code import save_sto_code
        r = save_sto_code()
        self.write("cron save sto code over, r:%s \n" % repr(r))

class CronUpdateStoCode(RequestHandler):
    def get(self):
        from data.sto_code import update_sto_code
        r = update_sto_code()
        self.write("cron update sto code over, r:%s \n" % repr(r))

class CronUpdateMarketCap(RequestHandler):
    def get(self):
        from capital_flow.market_cap import save_daily_market_cap
        r = save_daily_market_cap()
        self.write("cron daily update market cap over, r:%s \n" % repr(r))


common_handlers = [
    (r"/tmp_em", EMDataRequestHandler),
    # (r"/emUpdate", EMMarketCapUpdate),
]

cron_handlers = [
    (r"/cron/addStoCode", CronAddStoCode),
    (r"/cron/updateStoCode", CronUpdateStoCode),

    # 添加监控信号signal，当前的page_count, restart
    (r"/cron/updateMarketCap", CronUpdateMarketCap),
]

handlers = common_handlers + cron_handlers
