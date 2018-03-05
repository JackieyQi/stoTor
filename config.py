#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import os
import json
from tornado.options import options


class DBConfig(object):
    _cfg = json.loads(options.db)
 
    mysql_host = _cfg.get("mysql_host")
    mysql_user = _cfg.get("mysql_user")
    mysql_pwd = _cfg.get("mysql_pwd")

    redis_host = _cfg.get("redis_host")
    redis_port = _cfg.get("redis_port")


class SrvConfig(object): 
    _cfg = json.loads(options.db)

    email_sender = _cfg.get("email_sender")
    email_rcvr = _cfg.get("email_rcvr")
    email_pwd = _cfg.get("email_pwd")

CHROME_BROWSER_PATH = os.path.dirname(os.path.abspath("")) + "/chromedriver_linux64/chromedriver"

# easyMoney config
HSGTCG_EACH_PAGE_NUM = 50
NORTH_SHARE_HOLD_DAILY_COUNT = 6

# sto code type
STO_TURNOVER_TYPE_UP5 = 1
STO_TURNOVER = 500000000
STO_TURNOVER_COUNT = 6

# schedule config
SCHEDULE_JOBSTORES_URL = "mysql+pymysql://%s:%s@%s/stoADB"%(DBConfig.mysql_user, DBConfig.mysql_pwd, DBConfig.mysql_host)
EXECUTOR_POOL_THREADS = 10
EXECUTOR_POOL_PROCESSES = 5


