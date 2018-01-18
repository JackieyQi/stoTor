#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import pymysql
import redis


def get_cursor():
    user = 'root'
    pwd = '123456'
    cursor = pymysql.connect(host="localhost", user=user, passwd=pwd, db="stoADB", charset='utf8', use_unicode=False).cursor()
    cursor.execute("set @@autocommit=1")
    return cursor

def get_redis():
    pool = redis.ConnectionPool(host="redis", port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    return r
