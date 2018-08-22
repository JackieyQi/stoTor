#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado import web
from common.log import logger


class StoRequestHandler(RequestHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        sto_codes = self.get_argument("codes", "")
        if not sto_codes:
            sto_codes = self.get_self_sto_codes()

        print(sto_codes,type(sto_codes))
        logger.info("Sto request, {}, {}".format(sto_codes, type(sto_codes)))
        from spider.crawl import req_sina_stos
        r = req_sina_stos(sto_codes)
        self.write(r)
        self.finish()

    def get_self_sto_codes(self):
        return []


class EMMarketCapUpdate(RequestHandler):
    @gen.coroutine
    def get(self):
        from data.capital_flow.market_cap import save_single_sto
        r = save_single_sto("000001")
        self.write("update over, r:%s \n" % repr(r))


class SelfStoHandler(RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        from data.sto_code import opt_self_sto

        user_id, code = self.get_argument("user"), self.get_argument("code", "")
        if not user_id:
            return self.write({"result": False, "msg": "params err"})

        data = opt_self_sto(user_id, code, "")
        self.write({"result":True,"msg":data})

    @gen.coroutine
    def post(self):
        user_id, code, price = self.get_argument("user"), self.get_argument("code"), self.get_argument("price")
        top = self.get_argument("top")
        bot = self.get_argument("bot")
        if not user_id or not code or not price:
            return self.write({"result":False, "msg":"params err"})
        if not top:
            top = round(float(price)*1.05, 2)
        if not bot:
            bot = round(float(price)*0.95, 2)

        from data.sto_code import opt_self_sto
        msg = opt_self_sto(user_id, code, price, top, bot)
        self.write({"result":True,"msg":msg})

    @gen.coroutine
    def put(self):
        code, price = self.get_argument("code"), self.get_argument("price")
        if not code or not price:
            return self.write({"result":False, "msg":"params err"})
        from data.sto_code import opt_self_sto
        msg = opt_self_sto(code, price)
        self.write({"result":True,"msg":msg})


class LHBStoHandler(RequestHandler):
    def get(self):
        from data.capital_flow.billboard import LhBillboard
        r = LhBillboard().get_list_ratio()
        self.write("LHB Billboard data, %s" % repr(r))


class CommendStoHandler(RequestHandler):
    def get(self):
        from data.capital_flow.market_cap import get_market_cap_change_data
        a, _ = get_market_cap_change_data()
        self.write("commend data, %s" % repr(a))


class AdminUserHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        from data.user import admin_get_all_users

        key_code = self.get_argument("key", "")
        r = admin_get_all_users(key_code)
        self.write({"result": True, "users": r})


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
        from data.capital_flow.market_cap import save_daily_market_cap
        r = save_daily_market_cap(clear=True)
        self.write("cron daily update market cap over, r:%s \n" % repr(r))


class TestApi(RequestHandler):
    def get(self):
        from plot.real_analysis import send_morning_sum_email, send_trend_email
        #send_morning_sum_email()
        print("next func")
        send_trend_email()
        self.write("test api over")


common_handlers = [
    (r"/test", TestApi),
    (r"/sto", StoRequestHandler),
    # (r"/emUpdate", EMMarketCapUpdate),
    (r"/selfSto", SelfStoHandler),
    (r"/lhbSto", LHBStoHandler),
    (r"/commendSto", CommendStoHandler),

    (r"/admin/user", AdminUserHandler),
]

cron_handlers = [
    (r"/cron/stoCode", CronStoCode),
    (r"/cron/stoTurnover", CronStoTurnover),

    # 添加监控信号signal，当前的page_count, restart
    (r"/cron/marketCap", CronMarketCap),
]

handlers = common_handlers + cron_handlers
