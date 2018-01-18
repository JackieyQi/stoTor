#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-31
# @Author: yyq

from datetime import datetime, timedelta
from random import randint


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


def get_hour():
    return datetime.today().hour


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


def check_code_type(code):
    """
    note: sto code int to standard string
    """
    code = str(int(code))
    if len(code) == 6:
        return code
    else:
        code = "00000" + code
        return code[-6:]


def get_random(n=13):
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))
