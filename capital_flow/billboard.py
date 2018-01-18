#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import requests
from utils import get_time_inter

class LhBillboard(object):
    def __init__(self, top_time_inter=1):
        if top_time_inter not in (1, 3, 5):
            self.top_time_inter = 1
        else:
            self.top_time_inter = top_time_inter

        # self.em_url = "http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1," \
        #               "sortType=,startDate={},endDate={},gpfw=0,js=vardata_tab_1.html"
        self.em_url = "http://datainterface3.eastmoney.com//EM_DataCenter_V3/api/LHBGGDRTJ/GetLHBGGDRTJ?" \
                      "tkn=eastmoney&mkt=0&dateNum=&startDateTime={}7&endDateTime={}&sortRule=1&sortColumn=&pageNum=2&pageSize=200&cfg=lhbggdrtj"

    def get_top_list(self):
        start_date, end_date = get_time_inter(self.top_time_inter)

        resp = requests.get(self.em_url.format(start_date, end_date))
        if not resp:
            return
        data = resp.json().get("Data")[0].get("Data")
        # [0].get("FieldName")
        if len(data) == 0:
            return