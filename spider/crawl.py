#! /usr/bin/env python
# coding: utf8
# @Time: 18-07
# @Author: yyq

import requests
from common.utils import get_random


SINA_URL = "https://hq.sinajs.cn/rn={}&list={}"
CODE_URL = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php"

def req_sina_stos(sto_codes):
    if type(sto_codes) == type(list()):
        sto_codes = ",".join(sto_codes)
    result = {}

    resp = requests.get(SINA_URL.format(get_random(), sto_codes))
    if not resp:
        return result

    data_lst = resp.text.split("var hq_str_")
    for _d in data_lst:
        sto_str = _d.split(";\n")[0].split("=")
        if not sto_str[0]:
            continue

        code = sto_str[0][2:]
        _sto = {"code": code}
        for i, v in enumerate(sto_str[1].split(",")):
            if i == 0:
                _sto["name"] = v[1:]
            elif i == 3:
                _sto["price"] = v
            elif i == 8:
                _sto["count"] = str(int(float(v)/100))
            elif i == 9:
                _sto["amount"] = str(int(float(v)/10000))
        result[code] = _sto
    return result


def req_all_codes():
    result, count = dict(), 1
    while (count < 100):
        para_val = '[["hq","hs_a","",0,' + str(count) + ',500]]'
        r_params = {'__s': para_val}

        resp = requests.get(CODE_URL, params=r_params)
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

            result[code] = [name, symbol, money_amount]
        count += 1
    return result

 

#if __name__ == "__main__":
#    print(req_sina_stos(["sh600340", "sz000001"]))
