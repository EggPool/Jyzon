"""
Config file manager.
"""

import os.path as path
from logging import getLogger


__version__ = '0.0.1'

app_log = getLogger("tornado.application")



class Get:
    # "param_name":["type"] or "param_name"=["type","property_name"]
    vars = {"nyzoverifieripport": ["str"], "nyzopath": ["str"], "rpcuser": ["str"], "rpcpassword": ["str"],
            "loglevel": ["str"], "verbose": ["int"], "rpcport": ["int"]}

    def __init__(self):
        self.verbose = 0
        self.rpcport = 8444
        self.read()

    def load_file(self, filename):
        print("Loading", filename)
        for line in open(filename):
            if '=' in line:
                left, right = map(str.strip, line.rstrip("\n").split("="))
                if not left in self.vars:
                    # Warn for unknown param?
                    continue
                params = self.vars[left]
                if params[0] == "int":
                    right = int(right)
                elif params[0] == "list":
                    right = [item.strip() for item in right.split(",")]
                else:
                    # treat as "str"
                    pass
                if len(params) > 1:
                    # deal with properties that do not match the config name.
                    left = params[1]
                setattr(self, left, right)

    def read(self):
        # first of all, load from default config so we have all needed params
        self.load_file("jyzond.default.conf")
        # then override with optional custom config
        if path.exists("jyzond.conf"):
            self.load_file("jyzond.conf")
        # TODO: raise error if missing critical info like bismuth node/path
        # Better : raise in the client class, where we need it.
        if self.verbose:
            app_log.info(str(self.__dict__))
