#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-31
# @Author: yyq


def check_cap_unit(cap):
    if cap.find("亿") > -1:
        i = int(float(cap[:-1]) * 1000000)
        return i
    elif cap.find("万") > -1:
        i = int(float(cap[:-1]) * 100)
        return i
        # return float("%.7f" % i)
    else:
        return 0


def check_code_type(code):
    """
    note: sto code int to standard string
    """
    code = str(int(code))
    if len(code) == 6:
        return code
    else:
        code = "00000" + code
        return code[-6:]
