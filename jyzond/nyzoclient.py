"""
A basic Nyzo client for the Json-RPC gateway
@EggPool

"""

# Generic modules
import os
import sys
import threading
from time import time, sleep
from distutils.version import LooseVersion
from logging import getLogger
from asyncttlcache import Asyncttlcache


__version__ = "0.0.1"

# Interface versioning
API_VERSION = "0.1a"

"""
0.1a:  getinfo
"""

app_log = getLogger("tornado.application")


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
    )

    def __init__(self, config):
        try:
            self.config = config
            self.stop_event = threading.Event()
            self.frozen_edge = 0
            self.from_open = -1
            self._client_process = None
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

    def _poll(self):
        """
        Will ask the node for the new blocks/tx since last known state and run through filters
        :return:
        """
        app_log.info("Polling {}".format(self.frozen_edge))
        # TODO

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
