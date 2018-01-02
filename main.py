#! /usr/bin/env python
# coding: utf8
# @Time: 18-1-2
# @Author: yyq

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from views import handlers

tornado.options.define("port", default=8000, help="run on the port.", type=int)
tornado.options.define("ip", default="0.0.0.0", help="run on the address.", type=str)

def main():
    print("******************* starting server ******************")
    tornado.options.parse_command_line()

    app = tornado.web.Application(handlers=handlers, debug=False)
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(tornado.options.options.port, tornado.options.options.ip)

    tornado.ioloop.IOLoop.instance().start()