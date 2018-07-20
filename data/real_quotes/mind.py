#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-06
# @Author: yyq

import time
import json
import requests
from common.utils import get_random, get_today
from common.database import get_redis, get_cursor
from common.log import logger


class RealTimeStoData(object):
    def __init__(self, sto_lst):
        # eg:['sz000001', ]
        self.sto_codes = sto_lst

        self.redis = get_redis()

        self.url = "https://hq.sinajs.cn/rn={}&list={}"
        # current day data: datalen=48
        self.k_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?" \
                     "symbol={}&scale={}&ma=no&datalen=48"
        # real time money flow
        self.flow_url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssi_ssfx_flzjtj?daima={}"

    def get_real_data(self):
        resp = requests.get(self.url.format(get_random(), ",".join(self.sto_codes)))
        if not resp:
            return

        data_lst = resp.text.split("var hq_str_")
        for _d in data_lst:
            sto_str = _d.split(";\n")[0].split("=")
            if not sto_str[0]:
                continue

            sto_code = sto_str[0]
            for i, v in enumerate(sto_str[1].split(",")):
                if i == 0:
                    sto_name = v[1:]
                elif i == 3:
                    sto_price = v
                elif i == 8:
                    # 需要除以一百麽?
                    sto_count = v
                elif i == 9:
                    sto_money = v  # 需要除以一万麽？

    def save_k_data(self):
        for code_str in self.sto_codes:
        # k data 5 minutes
            r = self.get_k_data(code_str, scale=5)
            if r:
                logger.info("RealTimeStoData save_k_data, code:%s"%code_str)
                self.redis.rpush(code_str, r)

    def is_exist_k(self, code_str, r):
        last_r = self.redis.lindex(code_str, -1)
        if not last_r:
            return False

        if type(last_r) == bytes:
            last_r = json.loads(last_r.decode("utf8").replace("'",'"'))
        if r.get("day") == last_r.get("day"):
            return True
        else:
            return False

    def get_k_data(self, code_str, scale):
        resp = requests.get(self.k_url.format(code_str, scale))
        if not resp:
            logger.warning("RealTimeStoData get_k_data, request no response, code:%s"%code_str)
            return

        data = resp.text
        if str(get_today()) not in data:
            return

        r = dict()
        latest_data = data.split("},")[-2][:-1].split(':"')
        r["day"] = latest_data[1].split('"')[0]
        r["open"] = latest_data[2].split('"')[0]
        r["high"] = latest_data[3].split('"')[0]
        r["low"] = latest_data[4].split('"')[0]
        r["close"] = latest_data[5].split('"')[0]
        r["volume"] = latest_data[6].split('"')[0]

        if not self.is_exist_k(code_str, r):
            return r

    def get_flow_data(self):
        """
        "r0_": 特大单(元)
        "r1_": 大单
        "r2_": 中单
        "r3_": 散单
        "_in": 流入
        "_out": 流出
        "r0, r1, r2, r3": 成交量
        "curr_capital": 流通股值(万)
        "change_ratio": 涨跌幅
        "turnover_ratio": 换手率(*/10000)
        "net_amount": 净流入(元)
        """
        flow_data = dict()
        for code in self.sto_codes:
            resp = requests.get(self.flow_url.format(code))
            if not resp:
                continue
            data = resp.text

            r = dict()
            latest_data = data.split("},")[-1][:-1].split(':"')
            r["r0_in"] = latest_data[1].split('"')[0]
            r["r0_out"] = latest_data[2].split('"')[0]
            r["r0"] = latest_data[3].split('"')[0]
            r["r1_in"] = latest_data[4].split('"')[0]
            r["r1_out"] = latest_data[5].split('"')[0]
            r["r1"] = latest_data[6].split('"')[0]
            r["r2_in"] = latest_data[7].split('"')[0]
            r["r2_out"] = latest_data[8].split('"')[0]
            r["r2"] = latest_data[9].split('"')[0]
            r["r3_in"] = latest_data[10].split('"')[0]
            r["r3_out"] = latest_data[11].split('"')[0]
            r["r3"] = latest_data[12].split('"')[0]
            r["curr_capital"] = latest_data[13].split('"')[0]
            # r["name"] = latest_data[14].split('"')[0]
            # r["trade"] = latest_data[15].split('"')[0]
            r["change_ratio"] = latest_data[16].split('"')[0]
            # r["volume"] = latest_data[17].split('"')[0]
            r["turnover_ratio"] = latest_data[18].split('"')[0]
            # r["r0x_ratio"] = latest_data[19].split('"')[0]
            r["net_amount"] = latest_data[20].split('"')[0]
            r["time"] = int(time.time())
            flow_data[code] = r
        return flow_data


class RealTimeAnalysis(object):
    def __init__(self):
        pass

    def analysis_k_data(self):
        self._analysis_k_data(self.__reduce__())

    def _analysis_k_data(self, data):
        pass


def save_k_data():
    from data.sto_code import self_sto_pools

    sto_codes = list()
    for code in self_sto_pools.keys():
        if code[0] == "6":
            code_str = "sh"+code
        elif code[0] in ("0", "2"):
            code_str = "sz"+code
        else:
            code_str = code
        sto_codes.append(code_str)
    logger.info("save_k_data, sto_codes:%s" % sto_codes)
    RealTimeStoData(sto_codes).save_k_data()


def clear_k_data():
    from data.sto_code import self_sto_pools

    redis = get_redis()
    for code in self_sto_pools.keys():
        if code[0] == "6":
            code_str = "sh"+code
        elif code[0] in ("0", "2"):
            code_str = "sz"+code
        else:
            code_str = code
        r = redis.delete(code_str)
        logger.info("clear_k_data, key:%s, r:%s"%(code_str, r))


def save_flow_data():
    flow_data = RealTimeStoData(sto_codes).get_k_data()

    redis = get_redis()
    for code, v in flow_data.items():
        redis.rpush(code + "_flow", v)
