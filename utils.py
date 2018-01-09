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
