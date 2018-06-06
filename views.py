#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado import web


class StoRequestHandler(RequestHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        codes = self.get_argument("codes")
        print(codes,type(codes))
        #http_client = AsyncHTTPClient()
        #resp = yield http_client.fetch("http://hq.sinajs.cn/list=%s" % codes)
        #from real_quotes.mind import save_k_data
        #save_k_data()

        from message.squeues import email
        #email.delay("ttttttttttt","mmmmmmmmmmmmmmmmmm")
        resp = yield gen.Task(email.apply_async, args=["x_title", "y_msg"])
        self.write("result: %s" % 'sss')


class EMMarketCapUpdate(RequestHandler):
    @gen.coroutine
    def get(self):
        from capital_flow.market_cap import save_single_sto
        r = save_single_sto("000001")
        self.write("update over, r:%s \n" % repr(r))


class SelfStoHandler(RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        from data.sto_code import opt_self_sto
        code = self.get_argument("code", "")
        data = opt_self_sto(code, "")
        self.write({"result":True,"msg":data})

    @gen.coroutine
    def post(self):
        code, price = self.get_argument("code"), self.get_argument("price")
        top = self.get_argument("top", round(float(price)*1.05,2))
        bot = self.get_argument("bot", round(float(price)*0.95,2))

        from data.sto_code import opt_self_sto
        msg = opt_self_sto(code, price, top, bot)
        self.write({"result":True,"msg":msg})

    @gen.coroutine
    def put(self):
        code, price = self.get_argument("code"), self.get_argument("price")
        from data.sto_code import opt_self_sto
        msg = opt_self_sto(code, price)
        self.write({"result":True,"msg":msg})


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


class CronStoCode(RequestHandler):
    def put(self):
        from data.sto_code import save_sto_code
        r = save_sto_code()
        self.write("cron save sto code over, r:%s \n" % repr(r))


class CronStoTurnover(RequestHandler):
    def put(self):
        from data.sto_code import save_sto_turnover
        r = save_sto_turnover()
        self.write("cron save sto turnoer over, r:%s \n" % repr(r))


class CronMarketCap(RequestHandler):
    def put(self):
        from capital_flow.market_cap import save_daily_market_cap
        r = save_daily_market_cap(clear=True)
        self.write("cron daily update market cap over, r:%s \n" % repr(r))


common_handlers = [
    (r"/sto", StoRequestHandler),
    # (r"/emUpdate", EMMarketCapUpdate),
    (r"/selfSto", SelfStoHandler),
    (r"/lhbSto", LHBStoHandler),
    (r"/commendSto", CommendStoHandler),
]

cron_handlers = [
    (r"/cron/stoCode", CronStoCode),
    (r"/cron/stoTurnover", CronStoTurnover),

    # 添加监控信号signal，当前的page_count, restart
    (r"/cron/marketCap", CronMarketCap),
]

handlers = common_handlers + cron_handlers
