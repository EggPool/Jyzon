"""
A basic Nyzo client for the Json-RPC gateway
@EggPool

"""

# Generic modules
import os
import re
import sys
import threading
from time import time, sleep
from distutils.version import LooseVersion
from logging import getLogger
from asyncttlcache import Asyncttlcache
from pexpect import spawn, EOF, TIMEOUT

__version__ = "0.0.1"

# Interface versioning
API_VERSION = "0.1a"

"""
0.1a:  getinfo
"""

app_log = getLogger("tornado.application")

RE_VERSION = r"Nyzo client, version (\d+) "
RE_NODESCOUNT = r"NodeManager initialization: loaded (\d+) nodes into map"
RE_STATUS = r"frozen edge: (\d+), (\d+) from open"


class NyzoClient:
    """
    Connects to a verifier via the ejava client app and uses local filesystem if needed to interact with a running Nyzo verifier.
    """

    __slots__ = (
        "config",
        "stop_event",
        "frozen_edge",
        "from_open",
        "watchdog_thread",
        "poll",
        "_client_process",
        "client_version"
    )

    def __init__(self, config):
        try:
            self.config = config
            self.stop_event = threading.Event()
            self.frozen_edge = 0
            self.from_open = -1
            self._client_process = None
            self.client_version = 0
        except Exception as e:
            print("conn0", e)
        try:
            # config may not know of poll, that's ok.
            self.poll = self.config.poll
        except:
            self.poll = True
        # TODO: raise error if missing critical info like node/path
        """
        verifier_ip, verifier_port = self.config.nyzoverifieripport.split(":")
        try:
            # self.connection = Connection((node_ip, int(node_port)), verbose=config.verbose)
        except Exception as e:
            print("conn", e)
        """
        try:
            self.watchdog_thread = threading.Thread(target=self._watchdog)
            self.watchdog_thread.daemon = True
            self.watchdog_thread.start()
        except Exception as e:
            print("conn2", e)

    def _client_gone(self):
        self._client_process = None
        self.client_version = 0

    def _create_client_process(self):
        start = time()
        self._client_process = spawn("/usr/bin/env python3 ../mockup/mockup.py")
        index = self._client_process.expect([TIMEOUT, RE_VERSION, EOF])
        #print("Index", index)
        #print(self._client_process.after)
        #print(self._client_process.match)
        if index == 1:
            # print(self._client_process.match.groups())
            self.client_version = self._client_process.match.groups()[0].decode("utf-8")
        else:
            self._client_gone()
            return
        # print(self.client_version)
        app_log.info("Connected to client version {}, waiting for init...".format(self.client_version))
        # TODO: add a check for ok versions (compatible, high enough)
        index = self._client_process.expect([TIMEOUT, RE_NODESCOUNT, EOF])
        if index == 1:
            # print(self._client_process.match.groups())
            nodes_count = self._client_process.match.groups()[0].decode("utf-8")
        else:
            self._client_gone()
            return
        app_log.info("NodeManager initialization: loaded {} nodes into map".format(nodes_count))
        index = self._client_process.expect([TIMEOUT, RE_STATUS, EOF])
        if index == 1:
            init_time = time() - start
            # print(self._client_process.match.groups())
            self.frozen_edge = int(self._client_process.match.groups()[0].decode("utf-8"))
            self.from_open = int(self._client_process.match.groups()[1].decode("utf-8"))
        else:
            self._client_gone()
            return
        app_log.info("NodeManager initialization completed in {:0.2f} sec.".format(init_time))
        app_log.info("frozen edge: {}, {} from open".format(self.frozen_edge, self.from_open))

    def _poll(self):
        """
        Will ask the node for the new blocks/tx since last known state and run through filters
        :return:
        """
        # app_log.info("Polling {}".format(self.frozen_edge))
        if self._client_process is None:
            self._create_client_process()
        if self._client_process is None:
            app_log.error("Unable to create client process")
            return
        self._client_process.sendline("")
        index = self._client_process.expect([TIMEOUT, RE_STATUS, EOF])
        if index == 1:
            self.frozen_edge = int(self._client_process.match.groups()[0].decode("utf-8"))
            self.from_open = int(self._client_process.match.groups()[1].decode("utf-8"))
        else:
            self._client_gone()
        app_log.info("frozen edge: {}, {} from open".format(self.frozen_edge, self.from_open))


    def _watchdog(self):
        """
        called in a thread to send ping and poll the node if needed.
        :return:
        """
        # Give it some time to start and do things
        sleep(10)
        while not self.stop_event.is_set():
            if self.poll:
                self._poll()
            # is 10 sec is a good compromise?
            sleep(10)

    """
    All json-rpc calls are directly mapped to async methods here thereafter:
    As the mapping is auto, we can't conform to PEP and thus, no underscore in method names.
    """

    def stop(self, *args, **kwargs):
        """Clean stop the server"""
        app_log.info("Stopping Server")
        # self.connection.close()
        # TODO: Close possible open files and db connection
        #
        # TODO: Signal possible threads to terminate and wait.
        self.stop_event.set()
        # self.watchdog_thread.join() It's a daemon thread, no need to wait,
        # it can take up to 10 sec because of the sleep()
        return True
        # NOT So simple. Have to signal tornado app to close (and not leave the port open) see
        # https://stackoverflow.com/questions/5375220/how-do-i-stop-tornado-web-server
        # https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
        # sys.exit()

    @Asyncttlcache(ttl=5)
    async def getinfo(self, *args, **kwargs):
        """
        Returns a dict with the verifier info
        Could take a param like verbosity of returned info later.
        """
        # WARNING: getinfo is deprecated and will be fully removed in 0.16.
        # Projects should transition to using getblockchaininfo, getnetworkinfo,
        # and getwalletinfo before upgrading to 0.16
        # However we get all info in one go,
        # and it can be cached for subsequent partial info requests from other listed commands.
        info = dict()
        try:
            # bitcoind alike
            info["timeoffset"] = 0
            info["blocks"] = self.frozen_edge
            # add extra info
            info["fromopen"] = self.from_open
            info["version"] = self.config.version
            info["errors"] = ""
            info["testnet"] = False
        except Exception as e:
            info = {"version": self.config.version, "error": str(e)}
        return info
