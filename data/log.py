#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-18
# @Author: yyq

import os
import logging
import logging.handlers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger("sto_log")
# _handler = logging.FileHandler(BASE_DIR + "/log/sto.log")
log_handler = logging.handlers.TimedRotatingFileHandler(BASE_DIR + "/log/sto.log", when="D")
log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(log_handler)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.INFO)
