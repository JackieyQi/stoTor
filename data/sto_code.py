#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import json
import requests
from config import CFG
# from config import STO_TURNOVER, STO_TURNOVER_TYPE_UP5, STO_TURNOVER_COUNT
from common.database import get_cursor, get_redis
from common.log import logger
from common.utils import (code_int2str, check_sto_turnover, get_today, get_today_time, get_time_now, parse_price, unparse_price)
from spider.crawl import req_all_codes

self_sto_pools = dict()


class StoCode(object):
    def __init__(self, code="", price_in="", price_out="", price_top="", price_bot="", time_in=get_time_now()):
        self.code = code
        self.price_in_str = price_in
        self.price_out_str = price_out
        self.price_top_str = price_top
        self.price_bot_str = price_bot
        self.time_in = time_in

        self.cursor = get_cursor()
        self.redis = get_redis()


    def __str__(self):
        return json.dumps({"code":self.code,"price_in":self.price_in_str,"price_out":self.price_out_str,"top":self.price_top_str, "bot":self.price_bot_str, "time_in":self.time_in})

    def is_exist_opt(self):
        if self.cursor.execute("select id from user_sto where code=%s"%self.code):
            return True
        else:
            return False

    def add(self, top, bot):
        self.price_top_str = str(top)
        self.price_bot_str = str(bot)
        if self.is_exist_opt():
            self.cursor.execute("update user_sto set price_in=%s,price_top=%s,price_bot=%s,time_in=%s where code='%s';"%(parse_price(self.price_in_str), parse_price(top), parse_price(bot), self.time_in, self.code))
            msg = "self sto in update, code:%s"%self.code
        else:
            self.cursor.execute("insert into user_sto (code, price_in, price_top, price_bot, time_in) values('%s', %s, %s, %s, %s);"%(self.code, parse_price(self.price_in_str), parse_price(top), parse_price(bot), self.time_in))
            msg = "self sto in insert, code:%s"%self.code
        return msg

    def out(self, price):
        self.price_out_str = str(price)

        if self.is_exist_opt():
            self.cursor.execute("update user_sto set price_out=%s,time_out=%s where code='%s';"%(parse_price(price), get_time_now(), self.code))
            msg = "self sto out over, code:%s"%self.code
        else:
            msg = "err self sto out, not exist, code:%s"%self.code
        return msg


def save_sto_code():
    data = req_all_codes()
    if not data: return False

    in_data = list()
    for k, v in data.items():
        name, symbol, money_amount = v
        stype = check_sto_turnover(money_amount)
        in_data.append([k, name, symbol, stype])

    sql = "insert ignore into sto_code (code, name, symbol, type) values (%s, %s, %s, %s);"
    cursor = get_cursor()
    cursor.executemany(sql, in_data)
    cursor.close()
    return True


def save_sto_turnover():
    cursor = get_cursor()
    today_time = get_today_time()
    r = cursor.execute("select id from sto_src_turnover where create_time = %s limit 1;" % today_time)
    if r > 0: return True

    data = req_all_codes()
    logger.info("save_sto_turnover all sto code data len:%s" % len(data))
    if not data: return False

    in_data = list()
    for k, v in data.items():
        name, symbol, money_amount = v
        in_data.append([k, symbol, money_amount, today_time])

    sql = "insert into sto_src_turnover (code, symbol, turnover, create_time) values (%s, %s, %s, %s);"
    cursor.executemany(sql, in_data)

    count = cursor.execute("select create_time from sto_src_turnover where code = '000001';")
    if count > CFG.STO_TURNOVER_COUNT:
        db_data = list(cursor.fetchall())
        db_data.sort()
        _time = db_data[-CFG.STO_TURNOVER_COUNT][0]
        cursor.execute("delete from sto_src_turnover where create_time < %s;" % _time)
        count = CFG.STO_TURNOVER_COUNT

    cursor.execute("UPDATE sto_code set type=0 where type = %s;" % CFG.STO_TURNOVER_TYPE_UP5)
    sql = "UPDATE sto_code set type = %s  WHERE code in (SELECT code from (SELECT code, SUM(turnover)/%s as s " \
          "FROM `sto_src_turnover` GROUP BY code) as B where B.s > %s);" % (CFG.STO_TURNOVER_TYPE_UP5, count, CFG.STO_TURNOVER)
    cursor.execute(sql)

    cursor.close()
    logger.info("save_sto_turnover over, exist count:%s" % count)
    return True


def opt_self_sto(code, price, top="", bot=""):
    global self_sto_pools

    if price == "":
        if code not in self_sto_pools:
            return [str(v) for v in self_sto_pools.values()]
        else:
            return [str(self_sto_pools.get(code))]

    elif top == "":
        sto = self_sto_pools.get(code)
        if not sto:
            return "out err, no sto in cache, code:%s"%code
        msg = sto.out(price)
        del self_sto_pools[code]

    else:
        sto = self_sto_pools.get(code, StoCode(code, price_in=price))
        msg = sto.add(top, bot)
        self_sto_pools[code] = sto
    return msg

def load_self_sto():
    cursor = get_cursor()
    cursor.execute("select code, price_in, price_top, price_bot, time_in from user_sto where time_out != 0;")

    global self_sto_pools
    for d in cursor.fetchall():
        code, price_in, top, bot, date_in = d
        self_sto_pools[code] = StoCode(code, unparse_price(price_in), price_top=unparse_price(top), price_bot=unparse_price(bot), time_in=time_in)
    logger.info("load_self_sto over, len:%s"%len(self_sto_pools))


def init_sto_data():
    cursor = get_cursor()
    cursor.execute("select code, price_in, price_top, price_bot, time_in from user_sto where time_out != 0;")
    global self_sto_pools
    for d in cursor.fetchall():
        code, price_in, top, bot, time_in = d
        self_sto_pools[code] = StoCode(code, unparse_price(price_in), price_top=unparse_price(top), price_bot=unparse_price(bot), time_in=time_in)
    logger.info("init_sto_data, load self sto, len:%s"%len(self_sto_pools))

    sql = "select code from sto_code where type = %s;" % CFG.STO_TURNOVER_TYPE_UP5
    cursor.execute(sql)
    db_data = cursor.fetchall()
    count = 0
    redis = get_redis()
    redis.delete("up5Sto")
    for d in db_data:
        code = code_int2str(d[0])
        count += redis.sadd("up5Sto", code)
    logger.info("init_sto_data, init turnover up5, len:%s"%count)

