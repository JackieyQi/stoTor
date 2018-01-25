#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import requests
from config import STO_TURNOVER, STO_TURNOVER_TYPE_UP5, STO_TURNOVER_COUNT
from data.database import get_cursor
from data.log import logger
from utils import code_int2str, check_sto_turnover, get_today

upper_sto = list()


class StoCode(object):
    def __init__(self):
        self.sn_url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php"

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

    cursor.execute("UPDATE sto_code set type=0 where type = %s;" % STO_TURNOVER_TYPE_UP5)
    sql = "UPDATE sto_code set type = %s  WHERE code in (SELECT code from (SELECT code, SUM(turnover) as s " \
          "FROM `src_sto_turnover` GROUP BY code) as B where B.s > %s);" % (STO_TURNOVER_TYPE_UP5, STO_TURNOVER)
    cursor.execute(sql)

    cursor.close()
    logger.info("save_sto_turnover over, exist count:%s" % count)
    return True


def init_sto_data():
    cursor = get_cursor()
    global upper_sto
    upper_sto = list()

    sql = "select code from sto_code where type = %s;" % STO_TURNOVER_TYPE_UP5
    cursor.execute(sql)
    db_data = cursor.fetchall()
    for d in db_data:
        code = code_int2str(d[0])
        upper_sto.append(code)
