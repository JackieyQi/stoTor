#! /usr/bin/env python
# coding: utf8
# @Time: 18-02-08
# @Author: yyq
"""
config reset and run alone.
"""


from celery import Celery
from config import SrvConfig

#celery = Celery("stoMsgs", broker=broker_url, backend=backend_url)
celery_app = Celery("stoMsgs", broker=SrvConfig.celery_broker_url, backend=SrvConfig.celery_backend_url)

