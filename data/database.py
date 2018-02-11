#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import pymysql
import redis
from config import DBConfig


def get_cursor():
    cursor = pymysql.connect(host=DBConfig.mysql_host, user=DBConfig.mysql_user, passwd=DBConfig.mysql_pwd, db="stoADB", charset="utf8", use_unicode=True).cursor()
    cursor.execute("set @@autocommit=1")
    return cursor

def get_redis():
    pool = redis.ConnectionPool(host=DBConfig.redis_host, port=DBConfig.redis_port, db=0)
    r = redis.Redis(connection_pool=pool)
    return r

