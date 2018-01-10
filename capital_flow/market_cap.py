#! /usr/bin/env python
# coding: utf8
# @Time: 18-1-3
# @Author: yyq

"""
问题：全屏变量browser，多个请求调用，close是关哪一个，上下文相关？
"""

from selenium.webdriver.common.action_chains import ActionChains
from data.browser import SimulationChrome
from data.database import get_cursor
from utils import check_cap_unit, check_code_type


class NorthShareHold(object):
    def __init__(self, *args, **kwargs):
        self.browser = SimulationChrome().browser

        self.em_url = "http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?"
        self.single_url = "http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}"

    def del_browser(self):
        self.browser.quit()

    def get_north_data_daily(self, codes=None):
        self.browser.get(self.em_url)

        result, pre_length = dict(), 0
        while 1:
            ele = self.browser.find_element_by_id("tb_ggtj")
            ele_data = ele.text
            if len(ele_data) < 6:
                break
            data = ele_data.split("\n")[6:]

            while 1:
                _d = data[:3]
                if len(_d) < 3:
                    break
                sto_info = self.get_sto_info(_d)
                if codes:
                    if sto_info[0] not in codes:
                        continue

                # check duplicate web page.
                if sto_info[0] in result:
                    break
                result[sto_info[0]] = sto_info
                data = data[3:]

            if len(result) == pre_length:
                break
            pre_length = len(result)

            ele = self.browser.find_element_by_partial_link_text("下一页")
            ActionChains(self.browser).move_to_element(ele).click().perform()
        return list(result.values())

    def get_sto_info(self, data):
        """
        :param data: ['2017-12-19 600519', '贵州茅台', '详细 数据 667.09 0.20 7306.33万 487.40亿 5.60 8180.53万 1996.68万 51.32亿']
        :return:
        """
        ind_0, sto_name, ind_2 = data[0].split(" "), data[1], data[2].split(" ")
        date, sto_code = ind_0[0], ind_0[1]
        sto_price, sto_up = ind_2[2], ind_2[3] + "%"
        sto_day_1, sto_day_5, sto_day_10 = check_cap_unit(ind_2[7]), check_cap_unit(ind_2[8]), check_cap_unit(ind_2[9])
        return sto_code, sto_day_1, sto_day_5, sto_day_10, date
        # return {sto_code: {"date": date, "name": sto_name, "code": sto_code, "price": sto_price, "up": sto_up,
        #                    "day_1": sto_day_1, "day_5": sto_day_5, "day_10": sto_day_10}}

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
    sto_codes = list()
    cursor.execute("select code from sto_code where code >= 600000 and code < 700000;")
    db_data = cursor.fetchall()
    for _d in db_data:
        sto_code = check_code_type(_d[0])
        sto_codes.append(sto_code)

    # 深市A股，中小板
    cursor.execute("select code from sto_code where code < 2999;")
    db_data = cursor.fetchall()
    for _d in db_data:
        sto_code = check_code_type(_d[0])
        sto_codes.append(sto_code)

    _handler = NorthShareHold()
    data = _handler.get_north_data_daily(sto_codes)
    _handler.del_browser()
    if not data: return False

    sql = "insert into market_cap (code, cap1, cap5, cap10, date) values (%s, %s, %s, %s, %s);"
    cursor.executemany(sql, data)
    cursor.close()

    check_extra_daily_market_cap()
    return True

def check_extra_daily_market_cap():
    """
    note: only save 6 data to db.
    """
    cursor = get_cursor()
    count = cursor.execute("select date from market_cap where code = '000001';")
    if count <= 6:
        cursor.close()
        return False
    db_data = list(cursor.fetchall())
    db_data.reverse()
    _date = db_data[5]
    cursor.execute("delete from market_cap where date < %s;" % _date)
    cursor.close()
    return True
