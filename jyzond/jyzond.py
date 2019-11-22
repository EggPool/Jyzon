#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A bitcoind compatible rpc-server for NyzoVerifier client

(c) EggdraSyl - EggPool.net

"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from os import path

from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.web import Application

# custom modules
import rpcconfig
from nyzoclient import NyzoClient
from jsonrpchandler import JSONRPCHandler


__version__ = "0.0.1"


if __name__ == "__main__":

    rpc_config = rpcconfig.Get()
    # add our current code version
    rpc_config.version = __version__

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    app_log = logging.getLogger("tornado.application")
    enable_pretty_logging()
    logfile = path.abspath("websocket_app.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotateHandler = RotatingFileHandler(logfile, "a", 512 * 1024, 10)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    rotateHandler.setFormatter(formatter)
    app_log.addHandler(rotateHandler)

    access_log = logging.getLogger("tornado.access")
    enable_pretty_logging()
    logfile2 = path.abspath("websocket_access.log")
    rotateHandler2 = RotatingFileHandler(logfile2, "a", 512 * 1024, 10)
    formatter2 = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    rotateHandler2.setFormatter(formatter2)
    access_log.addHandler(rotateHandler2)

    try:
        nyzo_client = NyzoClient(rpc_config)
    except Exception as e:
        # At launch, it's ok to close if the node is not available.
        # TODO: once started, disconnects and reconnects have to be taken care of seemlessly.
        app_log.error("Unable to connect to node :", e)
        sys.exit()

    # see http://www.tornadoweb.org/en/stable/httpserver.html#http-server for ssl
    # see http://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings for logging and such
    # see also http://www.tornadoweb.org/en/stable/guide/structure.html#the-application-object
    app = Application([(r"/", JSONRPCHandler, dict(interface=nyzo_client))])

    app_log.info("Starting rpc server on port {}".format(rpc_config.rpcport))
    app.listen(rpc_config.rpcport)

    IOLoop.current().start()
