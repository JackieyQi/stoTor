#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import requests
from utils import get_time_inter
from data.sto_code import upper_sto
from data.log import logger


class LhBillboard(object):
    def __init__(self, top_time_inter=1):
        self.top_time_inter = top_time_inter
        self.time_inter_min = 1
        self.time_inter_max = 14

        # self.em_url = "http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1," \
        #               "sortType=,startDate={},endDate={},gpfw=0,js=vardata_tab_1.html"
        self.lhb_daily_url = "http://datainterface3.eastmoney.com//EM_DataCenter_V3/api/LHBGGDRTJ/GetLHBGGDRTJ?" \
                             "tkn=eastmoney&mkt=0&dateNum=&startDateTime={}&endDateTime={}&sortRule=1&sortColumn=&pageNum=1&pageSize=200&cfg=lhbggdrtj"

    def get_top_list(self, time_inter):
        start_date, end_date = get_time_inter(time_inter)

        resp = requests.get(self.lhb_daily_url.format(start_date, end_date))
        if not resp:
            return
        data = resp.json().get("Data")[0].get("Data")
        if len(data) == 0:
            return

        r = dict()
        for d in data:
            lst = d.split("|")
            # change_ratio: -7.9184=>-7.92%
            # turnover_ratio: 1.57=>1.57%
            code, change_ratio, turnover_ratio = lst[0], lst[3], lst[4]
            if not self.check_list_data(code):
                continue

            if code not in r:
                r[code] = [[change_ratio, turnover_ratio], ]
            elif code in r:
                r[code].append([change_ratio, turnover_ratio])
        return start_date, end_date, r

    def check_list_data(self, code):
        if code[0] == "3":
            return False
        elif code not in upper_sto:
            return False
        else:
            return True

    def get_list_ratio(self):
        _r_min_start_date, _r_min_end_date, _r_min = self.get_top_list(self.time_inter_min)
        r_min = sorted(_r_min.items(), key=lambda x: len(x[1]), reverse=True)

        _r_max_start_date, _r_max_end_date, _r_max = self.get_top_list(self.time_inter_max)
        r_max = sorted(_r_max.items(), key=lambda x: len(x[1]), reverse=True)
        logger.info("capital_flow billboard lhb data, min:%s, max:%s" % (len(r_min), len(r_max)))

        key_code = list()
        for k, v in _r_max.items():
            if len(v) == 1:
                continue
            if k in _r_min:
                key_code.append(k)

        for k, v_lst in r_max[:10]:
            if len(v_lst) == 1:
                continue
            key_code.append(k)

        for k, v_lst in r_min[:5]:
            if len(v_lst) == 1:
                continue
            key_code.append(k)

        result = list()
        for code in key_code:
            if len(result) == 5:
                return
            elif code not in result:
                result.append(code)
        return {"min_date": [_r_min_start_date, _r_min_end_date],
                "max_date": [_r_max_start_date, _r_max_end_date],
                "result": result}
