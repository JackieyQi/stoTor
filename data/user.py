#! /usr/bin/env python
# coding: utf8

import json
from common.log import logger
from common.database import get_cursor


user_pools = dict()


class UserObj(object):
    def __init__(self, user_id, status, mail="", phone=""):
        self.user_id = user_id
        self.status = status
        self.mail = mail
        self.phone = phone

    def __str__(self):
        return json.dumps({"mail": self.mail, "phone": self.phone})


def init_user():
    cursor = get_cursor()
    cursor.execute("select id, mail, phone, status from user where status = 0;")

    global user_pools
    for d in cursor.fetchall():
        user_id, mail, phone, status = d
        user_pools[user_id] = UserObj(user_id, status, mail=mail, phone=phone)
    logger.info("init_user, users count:{}".format(len(user_pools)))

