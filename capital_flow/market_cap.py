#! /usr/bin/env python
# coding: utf8
# @Time: 18-1-3
# @Author: yyq

"""
问题：全屏变量browser，多个请求调用，close是关哪一个，上下文相关？
"""

from data.browser import SimulationChrome
from data.database import get_cursor
from utils import check_cap_unit


class NorthShareHold(object):
    def __init__(self, *args, **kwargs):
        self.browser = SimulationChrome().browser

        self.em_url = "http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?"
        self.single_url = "http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}"

    def del_browser(self):
        self.browser.quit()

    def get_north_data(self):
        self.browser.get(self.em_url)
        ele = self.browser.find_element_by_id("tb_ggtj")
        ele_data = ele.text
        if len(ele_data) < 6: return
        data = ele_data.split("\n")[6:]
        result_list = list()

        tmp_re = list()
        while 1:
            _d = data[:3]
            if len(_d) < 3:
                break
            cto_info = self.get_cto_info(_d)
            result_list.append(list(cto_info.values())[0])

            tmp_re.append(cto_info)

            data = data[3:]

        return result_list

    def get_cto_info(self, data):
        """
        :param data: ['2017-12-19 600519', '贵州茅台', '详细 数据 667.09 0.20 7306.33万 487.40亿 5.60 8180.53万 1996.68万 51.32亿']
        :return:
        """
        ind_0, cto_name, ind_2 = data[0].split(" "), data[1], data[2].split(" ")
        date, cto_code = ind_0[0], ind_0[1]
        cto_price, cto_up = ind_2[2], ind_2[3] + "%"
        cto_day_1, cto_day_5, cto_day_10 = ind_2[7], ind_2[8], ind_2[9]
        return {cto_code: {"date": date, "name": cto_name, "code": cto_code, "price": cto_price, "up": cto_up,
                           "day_1": cto_day_1, "day_5": cto_day_5, "day_10": cto_day_10}}

    def get_single_data(self, sto_code):
        """
        note: get last 6 days data
        :param sto_code:
        :return:
        """
        self.browser.get(self.single_url.format(sto_code))
        ele = self.browser.find_element_by_id("tb_cgtj")
        ele_data = ele.text
        if len(ele_data) < 6: return
        data = ele_data.split("\n")[6:]

        r = list()
        for _s in data[:6]:
            _d = _s.split(" ")
            date = _d[0]
            cap_1, cap_5, cap_10 = check_cap_unit(_d[-3]), check_cap_unit(_d[-2]), check_cap_unit(_d[-1])
            r.append((sto_code, cap_1, cap_5, cap_10, date))
        return r


def get_subset(data):
    # 依次取10,5,1的子集最大值
    c, c_day_10, result_day_10 = 0, 15, list()
    while 1:
        r = max(data, key=lambda x: check_cap_unit(x.get("day_10")))
        data.remove(r)
        result_day_10.append(r)
        c += 1
        if c == c_day_10:
            break

    c, c_day_5, result_day_5 = 0, 10, list()
    while 1:
        r = max(result_day_10, key=lambda x: check_cap_unit(x.get("day_5")))
        result_day_10.remove(r)
        result_day_5.append(r)
        c += 1
        if c == c_day_5:
            break

    c, c_day_1, result_day_1 = 0, 5, list()
    while 1:
        r = max(result_day_5, key=lambda x: check_cap_unit(x.get("day_1")))
        result_day_5.remove(r)
        result_day_1.append(r)
        c += 1
        if c == c_day_1:
            break

    return result_day_1


def get_sort_data():
    _handler = NorthShareHold()
    data = _handler.get_north_data()
    _handler.del_browser()
    # 去掉一个最大值
    r = max(data, key=lambda x: check_cap_unit(x.get("day_10")))
    data.remove(r)

    result = get_subset(data)
    print("r:%s" % result)


def save_single_sto(sto_code):
    cursor = get_cursor()
    _handler = NorthShareHold()
    data = _handler.get_single_data(sto_code)
    _handler.del_browser()
    if not data: return False

    sql = "insert into market_cap (code, cap1, cap5, cap10, date) values (%s, %s, %s, %s, %s);"
    cursor.executemany(sql, data)
    cursor.close()
    return True

def save_daily_market_cap():
    cursor = get_cursor()
    # 沪市A股
    cursor.execute("select code from sto_code where code >= 600000 and code < 700000;")
    db_data = cursor.fetchall()
    # 深市A股，中小板
    cursor.execute("select code from sto_code where code < 2999;")
    db_data = cursor.fetchall()


