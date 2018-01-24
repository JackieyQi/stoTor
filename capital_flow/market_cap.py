#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

"""
问题：全屏变量browser，多个请求调用，close是关哪一个，上下文相关？
"""

import numpy
from selenium.webdriver.common.action_chains import ActionChains
from data.browser import SimulationChrome
from data.database import get_cursor
from data.sto_code import upper_sto
from utils import check_cap_unit, code_int2str
from config import HSGTCG_EACH_PAGE_NUM, NORTH_SHARE_HOLD_DAILY_COUNT


class NorthShareHold(object):
    def __init__(self, *args, **kwargs):
        self.browser = SimulationChrome().browser

        self.em_url = "http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?"
        self.single_url = "http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}"

    def del_browser(self):
        self.browser.quit()

    def get_north_data_daily(self):
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

                # check duplicate web page.
                if sto_info[0] in result:
                    break
                result[sto_info[0]] = sto_info
                data = data[3:]

            print("NorthShareHold get_north_data_daily data len:%s" % len(result))
            if 0 < len(result)-pre_length < HSGTCG_EACH_PAGE_NUM:
                break
            pre_length = len(result)

            ele = self.browser.find_element_by_partial_link_text("下一页")
            ActionChains(self.browser).move_to_element(ele).click().perform()
        return result

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

    def get_single_data(self, sto_code):
        """
        note: get last NORTH_SHARE_HOLD_DAILY_COUNT days data
        :param sto_code:
        :return:
        """
        self.browser.get(self.single_url.format(sto_code))
        ele = self.browser.find_element_by_id("tb_cgtj")
        ele_data = ele.text
        if len(ele_data) < 6: return
        data = ele_data.split("\n")[6:]

        r = list()
        for _s in data[:NORTH_SHARE_HOLD_DAILY_COUNT]:
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

    _handler = NorthShareHold()
    all_data = _handler.get_north_data_daily()
    _handler.del_browser()

    data = list()
    for _key in all_data:
        if not 2999 < int(_key) < 600000:
            continue
        elif int(_key) >= 700000:
            continue

        data.append(all_data.get(_key))
    if not data: return False

    count = cursor.execute("SELECT id from market_cap where date='%s' LIMIT 1;"%data[0][-1])
    if count > 0:
        return True

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
    if count <= NORTH_SHARE_HOLD_DAILY_COUNT:
        cursor.close()
        return False
    db_data = list(cursor.fetchall())
    db_data.sort()
    _date = db_data[-NORTH_SHARE_HOLD_DAILY_COUNT][0]
    cursor.execute("delete from market_cap where date < '%s';" % _date)
    cursor.close()
    return True

def get_market_cap_change_data():
    cursor = get_cursor()
    cursor.execute("select * from market_cap;")

    r = dict()
    for d in cursor.fetchall():
        _, code, cap1, cap5, cap10, date = d
        if type(code) == bytes:
            code = code.decode("utf8")
        if code not in upper_sto:
            continue

        if code not in r:
            r[code] = [[cap1, cap5, cap10, date], ]
        else:
            r[code].append([cap1, cap5, cap10, date])

    final_r = list()
    _f = list()
    for k, v_lst in r.items():
        tf = get_market_cap_tend(k, v_lst)
        if tf:
            final_r.append(k)
        else:
            _f.append(k)
    return final_r, _f


def get_market_cap_tend(code, cap_lst):
    cap_lst.sort(key=lambda x:x[3])
    matrix = numpy.array(cap_lst)

    if matrix.shape[1] < NORTH_SHARE_HOLD_DAILY_COUNT:
        return False

    cap_1, cap_5, cap_10 = matrix[:, 0], matrix[:, 1], matrix[:, 2]
    if cap_10[-1] < 0:
        return False

    if cap_5[-2] - cap_5[-3] < 0:
        return False
    elif cap_5[-1] - cap_5[-2] <0:
        return False

    if cap_1[-1] > 0 and cap_1[-2] > 0:
        if cap_1[-2] - cap_1[-3] > 0 and cap_1[-1] - cap_1[-2] > 0:
            return True
    return False
