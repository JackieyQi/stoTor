#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-31
# @Author: yyq

import time
from datetime import datetime, timedelta
from random import randint
from config import CFG


def get_time_inter(inter=1):
    today = get_today()
    today_w = int(today.strftime("%w"))
    if today_w == 0:
        return str(today - timedelta(inter + 2)), str(today - timedelta(2))
    elif today_w == 6:
        return str(today - timedelta(inter + 1)), str(today - timedelta(1))
    else:
        if get_hour() >= 18: inter -= 1
        return str(today - timedelta(inter)), str(today)


def get_today():
    return datetime.today().date()


def get_today_time():
    return int(time.mktime(get_today().timetuple()))


def get_hour():
    return datetime.today().hour


def get_time_now():
    return int(time.time())


def get_stamp(date_str, form="%Y-%m-%d"):
    return int(time.mktime(datetime.strptime(date_str, form).timetuple()))


def parse_price(price):
    try:
        return int(round(float(price), 2) *100)
    except ValueError:
        return 0


def unparse_price(db_price):
    try:
        return str(db_price/100)
    except ValueError:
        return ""


def check_cap_unit(cap):
    if cap.find("亿") > -1:
        i = int(float(cap[:-1]) * 1000000)
        return i
    elif cap.find("万") > -1:
        i = int(float(cap[:-1]) * 100)
        return i
        # return float("%.7f" % i)
    else:
        return 0


def code_int2str(code):
    """
    note: sto code int to standard string
    """
    code = str(int(code))
    if len(code) == 6:
        return code
    else:
        code = "00000" + code
        return code[-6:]

def is_code_legal(code):
    if type(code) == int:
        return True, code_int2str(code)
    elif type(code) == str:
        pass


def get_random(n=13):
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))


def check_sto_turnover(value):
    if int(value) >= CFG.STO_TURNOVER:
        return CFG.STO_TURNOVER_TYPE_UP5
