#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-01
# @Author: yyq

import pymysql
import redis
from config import CFG


def get_cursor():
    cursor = pymysql.connect(host=CFG.db.mysql_host, user=CFG.db.mysql_user, passwd=CFG.db.mysql_pwd, db=CFG.db.mysql_db, charset="utf8", use_unicode=True).cursor()
    cursor.execute("set @@autocommit=1")
    return cursor

def get_redis():
    pool = redis.ConnectionPool(host=CFG.db.redis_host, port=CFG.db.redis_port, db=CFG.db.redis_db)
    r = redis.Redis(connection_pool=pool)
    return r

