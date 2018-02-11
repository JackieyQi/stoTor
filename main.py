#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

import os
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from data.log import logger
from views import handlers

tornado.options.define("port", default=8000, help="run on the port.", type=int)
tornado.options.define("ip", default="0.0.0.0", help="run on the address.", type=str)
tornado.options.define("db", default="", help="database configuration")


def main():
    print("******************* starting server ******************")
    logger.info("******************* starting server ******************")
    tornado.options.parse_config_file(os.path.abspath("")+"/gzrq.cfg")

    app = tornado.web.Application(handlers=handlers, debug=False)
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(tornado.options.options.port, tornado.options.options.ip)

    from data.sto_code import init_sto_data
    init_sto_data()

    from data.schedule import SScheduler
    SScheduler().init_main_job()

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
