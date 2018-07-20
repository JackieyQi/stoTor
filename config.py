#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

from collections import namedtuple

class Configuration(object):
    pass
CFG = Configuration()


def init_config(cfg):
    def set_config(d):
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = set_config(v)
        return namedtuple("CFG", d.keys())(*d.values())

    global CFG
    CFG = set_config(cfg)
