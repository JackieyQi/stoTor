#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import os
import json
# import tcelery
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from common.log import logger
from views import handlers

# tornado.options.define("cfg", default="", help="configuration", callback=lambda path:tornado.options.parse_config_file(os.path.abspath("")+"/gzrq.py", final=False))
tornado.options.define("cfg", default="", help="configuration")


def main():
    logger.info("******************* starting server ******************")
    print("******************* starting server ******************")
    tornado.options.parse_config_file(os.path.abspath("") + "/gzrq.py")

    from config import init_config
    init_config(json.loads(tornado.options.options.cfg))

    from config import CFG
    app = tornado.web.Application(handlers=handlers, debug=CFG.debug)
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(CFG.srv.port, CFG.srv.ip)

    # from message.scelery import celery_app
    # tcelery.setup_nonblocking_producer(celery_app=celery_app)

    from data.sto_code import init_sto_data
    init_sto_data()

    from message.schedule import SScheduler
    SScheduler().init_main_job()

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
