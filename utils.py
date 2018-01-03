#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-31
# @Author: yyq


def check_cap_unit(cap):
    if cap.find("亿") > -1:
        i = float(cap[:-1])
        return i
    elif cap.find("万") > -1:
        i = float(cap[:-1]) / 10000
        return float("%.7f" % i)
    else:
        return 0
