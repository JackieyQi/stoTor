#! /usr/bin/env python
# coding: utf8


import json
from common.database import get_redis
from common.log import logger
from message.semail import send_email


def get_redis_sto_keys():
    lst = []

    from data.sto_code import self_sto_pools
    for code in self_sto_pools.keys():
        if code[0] == "6":
            sto_code = "sh" + code
        elif code[0] in ("0", "2"):
            sto_code = "sz" + code
        else:
            sto_code = code
        lst.append(sto_code)
    return lst


def send_morning_sum_email():
    sto_keys = get_redis_sto_keys()

    result = []
    redis = get_redis()
    for k in sto_keys:
        v = redis.lrange(k, 0, 1)
        if not v:
            logger.error("send_morning_sum_email, redis no data, k:{}".format(k))
            result.append("<td> {k}</td> <td>{v}</td>".format(k=k, v="redis no data"))
            continue
        elif len(v) < 2:
            logger.error("send_morning_sum_email, redis less data, k:{}".format(k))
            result.append("<td> {k}</td> <td>{v}</td>".format(k=k, v="redis less data"))
            continue
        result.append("<td> {k}</td> <td>{v1}</td>"
                      "<tr/><td></td><td>{v2}</td>".format(k=k,
                                                          v1=json.loads(v[0]),
                                                          v2=json.loads(v[1])))


    logger.info("send_morning_sum_email over, k:{}".format(sto_keys))
    text = "<table border='1'><tr>" + "<tr/><tr/>".join(result) + "</tr></table>"
    return send_email(title="MorningSummary", msg=text)


def send_trend_email():
    sto_keys = get_redis_sto_keys()
    
    redis = get_redis()
    for k in sto_keys:
        v = redis.lrange(k, -4, -1)
        if not v:
            continue

        trend_c, trend_data = 0, []
        for _l in v:
            l_line = json.loads(_l)
            diff = float(l_line["close"]) - float(l_line["open"])
            if diff < 0:
                trend_c -= 1
            else:
                trend_c += 1
            trend_data.append(str(diff))

        if trend_c == -4:
            logger.info("RealTimeNotice, k:{}".format(k))
            trend_data.insert(0, k)
            text = "<br/><br/>".join(trend_data)
            send_email(title="RealTimeNotice", msg=text)

