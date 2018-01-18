#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-06
# @Author: yyq

import json
import requests
from utils import get_random, get_today
from data.database import get_redis


class RealTimeStoData(object):
    def __init__(self, sto_lst):
        # eg:['sz000001', ]
        self.sto_codes = sto_lst

        self.url = "https://hq.sinajs.cn/rn={}&list={}"
        # current day data: datalen=48
        self.k_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?" \
                     "symbol={}&scale={}&ma=no&datalen=48"

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
                elif i ==9:
                    sto_money = v # 需要除以一万麽？

    def get_k_data(self):
        # k data 5 minutes
        scale = 5
        k_data = dict()
        for code in self.sto_codes:
            resp = requests.get(self.k_url.format(code, scale))
            if not resp:
                # warnning log
                continue

            data = resp.text
            if str(get_today()) not in data:
                continue

            r = dict()
            latest_data = data.split("},")[-1][:-1].split(':"')
            r["day"] = latest_data[1].split('"')[0]
            r["open"] = latest_data[2].split('"')[0]
            r["high"] = latest_data[3].split('"')[0]
            r["low"] = latest_data[4].split('"')[0]
            r["close"] = latest_data[5].split('"')[0]
            r["volume"] = latest_data[6].split('"')[0]
            k_data[code] = r

            # data = json.loads(resp.text)[-1]
            # day = data.get("day")
        return k_data

    def save_k_data(self):
        data = self.get_k_data()


class RealTimeAnalysis(object):
    def __init__(self):
        pass

    def analysis_k_data(self):
        self._analysis_k_data(self.__reduce__())

    def _analysis_k_data(self, data):
        pass

def save_k_data():
    sto_codes = ["sz000001", "sh600000",]
    # _ = RealTimeStoData(sto_codes).save_k_data()
    k_data = RealTimeStoData(sto_codes).get_k_data()

    redis = get_redis()
    for code, v in k_data:
        redis.rpush(code, v)