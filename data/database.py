#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import pymysql


def get_cursor():
    user = 'root'
    pwd = '123456'
    cursor = pymysql.connect(host="localhost", user=user, passwd=pwd, db="stoADB", charset='utf8', use_unicode=False).cursor()
    cursor.execute("set @@autocommit=1")
    return cursor
