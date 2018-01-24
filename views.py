#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

# import tornado.gen
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen


class StoRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self, *args):
        http_client = AsyncHTTPClient()
        resp = yield http_client.fetch("http://hq.sinajs.cn/list=%s" % args)
        self.write("result: %s" % resp.text)


class EMMarketCapUpdate(RequestHandler):
    @gen.coroutine
    def get(self):
        from capital_flow.market_cap import save_single_sto
        r = save_single_sto("000001")
        self.write("update over, r:%s \n" % repr(r))


class LHBStoHandler(RequestHandler):
    def get(self):
        from capital_flow.billboard import LhBillboard
        r = LhBillboard().get_list_ratio()
        self.write("LHB Billboard data, %s" % repr(r))


class CommendStoHandler(RequestHandler):
    def get(self):
        from capital_flow.market_cap import get_market_cap_change_data
        a, _ = get_market_cap_change_data()
        self.write("commend data, %s" % repr(a))


class CronAddStoCode(RequestHandler):
    def get(self):
        from data.sto_code import save_sto_code
        r = save_sto_code()
        self.write("cron save sto code over, r:%s \n" % repr(r))


class CronUpdateMarketCap(RequestHandler):
    def get(self):
        from capital_flow.market_cap import save_daily_market_cap
        r = save_daily_market_cap()
        self.write("cron daily update market cap over, r:%s \n" % repr(r))


common_handlers = [
    (r"/sto", StoRequestHandler),
    # (r"/emUpdate", EMMarketCapUpdate),
    (r"/lhbSto", LHBStoHandler),
    (r"/commendSto", CommendStoHandler),
]

cron_handlers = [
    (r"/cron/addStoCode", CronAddStoCode),

    # 添加监控信号signal，当前的page_count, restart
    (r"/cron/updateMarketCap", CronUpdateMarketCap),
]

handlers = common_handlers + cron_handlers
