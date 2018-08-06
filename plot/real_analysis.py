#! /usr/bin/env python
# coding: utf8

from common.database import get_redis
from common.log import logger


def check_d():
    from data.sto_code import self_sto_pools
    
    redis = get_redis()
    for code in self_sto_pools.keys():
        if code[0] == "6":
            sto_code = "sh" + code
        elif code[0] in ("0", "2"):
            sto_code = "sz" + code
        else:
            sto_code = code

