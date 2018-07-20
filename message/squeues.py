#! /usr/bin/env python
# coding: utf8
# @Time: 18-02-08
# @Author: yyq

from message.scelery import celery_app
from common.log import logger
from message.semail import send_email


@celery_app.task
def email(title, msg, callback):
    logger.info("squeues task email start, title:%s"%title)
    callback(send_email(title, msg))

