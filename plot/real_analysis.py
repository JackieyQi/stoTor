#! /usr/bin/env python
# coding: utf8


import json
from common.database import get_redis
from common.log import logger
from message.semail import send_email, send_multi_emails


def get_redis_self_sto_keys():
    user_stos = {}

    from data.sto_code import self_sto_pools
    for user_id, stos in self_sto_pools.items():
        _stos = []
        for code in stos.keys():
            if code[0] == "6":
                sto_code = "sh" + code
            elif code[0] in ("0", "2"):
                sto_code = "sz" + code
            else:
                sto_code = code
            _stos.append(sto_code)
        user_stos[user_id] = _stos
    return user_stos


def send_morning_sum_email():
    user_stos = get_redis_self_sto_keys()

    sto_codes_data = {}
    redis = get_redis()
    for user_id, sto_codes in user_stos:
        for k in sto_codes:
            if k in sto_codes_data:
                continue

            v = redis.lrange(k, 0, 1)
            if not v:
                logger.error("send_morning_sum_email, redis no data, k:{}".format(k))
                # result.append("<td> {k}</td> <td>{v}</td>".format(k=k, v="redis no data"))
                continue
            elif len(v) < 2:
                logger.error("send_morning_sum_email, redis less data, k:{}".format(k))
                # result.append("<td> {k}</td> <td>{v}</td>".format(k=k, v="redis less data"))
                continue
            sto_codes_data[k] = v

    from data.user import user_pools
    user_msgs = {}
    for user_id, sto_codes in user_stos:
        if user_id not in user_pools:
            logger.error("send_morning_sum_email, user no exist:{}".format(user_id))
            continue
        user_email, user_result = user_pools.get(user_id).mail, []

        for k in sto_codes:
            v = sto_codes_data.get(k, ["{}", "{}"])
            user_result.append("<td> {k}</td> <td>{v1}</td>"
                      "<tr/><td></td><td>{v2}</td>".format(k=k,
                                                          v1=json.loads(v[0]),
                                                          v2=json.loads(v[1])))
        user_title = "MorningSummary"
        user_text = "<table border='1'><tr>" + "<tr/><tr/>".join(user_result) + "</tr></table>"
        user_msgs[user_email] = {"title": user_title, "text": user_text}


    if not user_msgs:
        return
    logger.info("send_morning_sum_email over, user:{}".format(user_msgs.keys()))
    return send_multi_emails(user_msgs=user_msgs)


def send_trend_email():
    sto_keys = get_redis_self_sto_keys()

    sto_codes_data = {}
    redis = get_redis()
    for user_id, sto_codes in user_stos:
        for k in sto_codes:
            if k in sto_codes_data:
                continue

            v = redis.lrange(k, -4, -1)
            if not v:
                continue
            sto_codes_data[k] = v

    from data.user import user_pools
    user_msgs = {}
    for user_id, sto_codes in user_stos:
        if user_id not in user_pools:
            logger.error("send_trend_email, user no exist:{}".format(user_id))
            continue
        user_email, user_result = user_pools.get(user_id).mail, []

        for k in sto_codes:
            v = sto_codes_data.get(k)

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
                trend_data.insert(0, k)
                user_result.extend(trend_data)

        user_title = "RealTimeNotice"
        user_text = "<br/><br/>".join(user_result)
        user_msgs[user_email] = {"title": user_title, "text": user_text}

    if not user_msgs:
        return
    logger.info("send_trend_email over, user:{}".format(user_msgs.keys()))
    return send_multi_emails(user_msgs=user_msgs)

