#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import requests
from data.database import get_cursor


class StoCode(object):
    def __init__(self):
        self.sn_url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php"

    def get_all_sto_code(self):
        result, count = [], 1
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
                code, name = i[0], i[2]
                symbol = ""
                if (code.find('sh') > -1):
                    code = code[2:]
                    symbol = "sh"
                    # code = code[2:] + '.SS'
                elif (code.find('sz') > -1):
                    code = code[2:]
                    symbol = "sz"
                    # code = code[2:] + '.SZ'

                # result.append({"symbol": code, "name": name})

                # type in database is int, not string
                code = int(code)
                result.append((code, name, symbol))
            count += 1
        return result


def save_sto_code():
    cursor = get_cursor()
    _handler = StoCode()
    data = _handler.get_all_sto_code()
    if not data: return False

    sql = "insert ignore into sto_code (code, name, symbol) values (%s, %s, %s);"
    cursor.executemany(sql, data)
    cursor.close()
    return True
