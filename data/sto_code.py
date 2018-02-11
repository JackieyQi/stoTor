#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import json
import requests
from config import STO_TURNOVER, STO_TURNOVER_TYPE_UP5, STO_TURNOVER_COUNT
from data.database import get_cursor, get_redis
from data.log import logger
from utils import code_int2str, check_sto_turnover, get_today

self_sto_pools = dict()


class StoCode(object):
    def __init__(self, code="", price_in="", price_out="", price_top="", price_bot="", date_in=None):
        self.code = code
        self.price_in_str = price_in
        self.price_out_str = price_out
        self.price_top_str = price_top
        self.price_bot_str = price_bot
        self.date_in = date_in

        self.cursor = get_cursor()
        self.redis = get_redis()

        self.sn_url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php"

    def __str__(self):
        return json.dumps({"code":self.code,"price_in":self.price_in_str,"price_out":self.price_out_str,"top":self.price_top_str, "bot":self.price_bot_str, "date_in":str(self.date_in)})

    def is_exist_opt(self):
        if self.cursor.execute("select id from self_sto where code=%s"%self.code):
            return True
        else:
            return False

    def add(self, top, bot):
        self.price_top_str = str(top)
        self.price_bot_str = str(bot)
        if self.is_exist_opt():
            self.cursor.execute("update self_sto set price_in=%s,price_top=%s,price_bot=%s,date_in='%s' where code='%s';"%(self.price_in_str, top, bot, self.date_in, self.code))
            msg = "self sto in update, code:%s"%self.code
        else:
            self.cursor.execute("insert into self_sto (code, price_in, price_top, price_bot, date_in) values('%s', %s, %s, %s, '%s');"%(self.code, self.price_in_str, top, bot, self.date_in)) 
            msg = "self sto in insert, code:%s"%self.code
        return msg

    def out(self, price):
        date = get_today()
        self.price_out_str = str(price)

        if self.is_exist_opt():
            self.cursor.execute("update self_sto set price_out=%s,date_out='%s' where code='%s';"%(price, date, self.code))
            msg = "self sto out over, code:%s"%self.code
        else:
            msg = "err self sto out, not exist, code:%s"%self.code
        return msg

    def get_all_sto_code(self):
        result, count = dict(), 1
        while (count < 100):
            para_val = '[["hq","hs_a","",0,' + str(count) + ',500]]'
            r_params = {'__s': para_val}
            resp = requests.get(self.sn_url, params=r_params)

            if not resp:
                count += 1
                continue
            _data = resp.json()[0].get("items", [])
            if len(_data) == 0:
                break
            for i in _data:
                code_str, name, money_amount = i[0], i[2], i[13]
                symbol = ""
                if (code_str.find('sh') > -1):
                    code = code_str[2:]
                    symbol = "sh"
                elif (code_str.find('sz') > -1):
                    code = code_str[2:]
                    symbol = "sz"

                result[int(code)] = [name, symbol, money_amount]
            count += 1
        return result


def save_sto_code():
    cursor = get_cursor()
    _handler = StoCode()
    data = _handler.get_all_sto_code()
    if not data: return False

    in_data = list()
    for k, v in data.items():
        name, symbol, money_amount = v
        type = check_sto_turnover(money_amount)
        in_data.append([k, name, symbol, type])

    sql = "insert ignore into sto_code (code, name, symbol, type) values (%s, %s, %s, %s);"
    cursor.executemany(sql, in_data)
    cursor.close()
    return True


def save_sto_turnover():
    cursor = get_cursor()
    date = get_today()
    r = cursor.execute("select id from src_sto_turnover where date = '%s' limit 1;" % date)
    if r > 0: return True

    data = StoCode().get_all_sto_code()
    logger.info("save_sto_turnover all sto code data len:%s" % len(data))
    if not data: return False

    in_data = list()
    for k, v in data.items():
        name, symbol, money_amount = v
        in_data.append([k, symbol, money_amount, date])

    sql = "insert into src_sto_turnover (code, symbol, turnover, date) values (%s, %s, %s, %s);"
    cursor.executemany(sql, in_data)

    count = cursor.execute("select date from src_sto_turnover where code = 1;")
    if count > STO_TURNOVER_COUNT:
        db_data = list(cursor.fetchall())
        db_data.sort()
        _date = db_data[-STO_TURNOVER_COUNT][0]
        cursor.execute("delete from src_sto_turnover where date < '%s';" % _date)
        count = STO_TURNOVER_COUNT

    cursor.execute("UPDATE sto_code set type=0 where type = %s;" % STO_TURNOVER_TYPE_UP5)
    sql = "UPDATE sto_code set type = %s  WHERE code in (SELECT code from (SELECT code, SUM(turnover)/%s as s " \
          "FROM `src_sto_turnover` GROUP BY code) as B where B.s > %s);" % (STO_TURNOVER_TYPE_UP5, count, STO_TURNOVER)
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
        sto = self_sto_pools.get(code, StoCode(code, price_in=price, date_in=get_today()))
        msg = sto.add(top, bot)
        self_sto_pools[code] = sto
    return msg

def load_self_sto():
    cursor = get_cursor()
    cursor.execute("select code, price_in, price_top, price_bot, date_in from self_sto where date_out is null;")

    global self_sto_pools
    for d in cursor.fetchall():
        code, price_in, top, bot, date_in = d
        self_sto_pools[code] = StoCode(code, price_in, price_top=top, price_bot=bot, date_in=date_in)
    logger.info("load_self_sto over, len:%s"%len(self_sto_pools))


def init_sto_data():
    cursor = get_cursor()
    cursor.execute("select code, price_in, price_top, price_bot, date_in from self_sto where date_out is null;")
    global self_sto_pools
    for d in cursor.fetchall():
        code, price_in, top, bot, date_in = d
        self_sto_pools[code] = StoCode(code, price_in, price_top=top, price_bot=bot, date_in=date_in)
    logger.info("init_sto_data, load self sto, len:%s"%len(self_sto_pools))

    sql = "select code from sto_code where type = %s;" % STO_TURNOVER_TYPE_UP5
    cursor.execute(sql)
    db_data = cursor.fetchall()
    count = 0
    redis = get_redis()
    redis.delete("up5Sto")
    for d in db_data:
        code = code_int2str(d[0])
        count += redis.sadd("up5Sto", code)
    logger.info("init_sto_data, init turnover up5, len:%s"%count)

