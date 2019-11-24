# coding=utf-8

"""
A basic Nyzo client for the Json-RPC gateway
@EggPool

"""

import re, sys, os
from threading import Thread, Lock, Event
from time import time, sleep
# from distutils.version import LooseVersion
from logging import getLogger
from asyncttlcache import Asyncttlcache
from pexpect import spawn, EOF, TIMEOUT
from tornado.ioloop import IOLoop

__version__ = "0.0.1"

# Interface versioning
API_VERSION = "0.1b"

"""
0.1a:  getinfo
0.1b:  getbalancebyaddress
"""

app_log = getLogger("tornado.application")

RE_VERSION = r"Nyzo client, version (\d+) "
RE_NODESCOUNT = r"NodeManager initialization: loaded (\d+) nodes into map"
RE_STATUS = r"frozen edge: (\d+), (\d+) from open"
RE_BALANCE = r"\xe2\x95\x91 (\d+) \xe2\x95\x91 (.+) \xe2\x95\x91 id__(.+) \xe2\x95\x91 \xe2\x88\xa9(.+) \xe2\x95\x91"


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
        "client_version",
        "_query_lock"
    )

    def __init__(self, config):
        try:
            self.config = config
            self.stop_event = Event()
            self._query_lock = Lock()
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
        try:
            self.watchdog_thread = Thread(target=self._watchdog)
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
        # print("Index", index)
        # print(self._client_process.after)
        # print(self._client_process.match)
        if index == 1:
            # print(self._client_process.match.groups())
            self.client_version = self._client_process.match.groups()[0].decode("utf-8")
        else:
            self._client_gone()
            return
        # print(self.client_version)
        app_log.info(
            "Connected to client version {}, waiting for init...".format(
                self.client_version
            )
        )
        # TODO: add a check for ok versions (compatible, high enough)
        index = self._client_process.expect([TIMEOUT, RE_NODESCOUNT, EOF])
        if index == 1:
            # print(self._client_process.match.groups())
            nodes_count = self._client_process.match.groups()[0].decode("utf-8")
        else:
            self._client_gone()
            return
        app_log.info(
            "NodeManager initialization: loaded {} nodes into map".format(nodes_count)
        )
        index = self._client_process.expect([TIMEOUT, RE_STATUS, EOF])
        if index == 1:
            init_time = time() - start
            # print(self._client_process.match.groups())
            self.frozen_edge = int(
                self._client_process.match.groups()[0].decode("utf-8")
            )
            self.from_open = int(self._client_process.match.groups()[1].decode("utf-8"))
        else:
            self._client_gone()
            return
        app_log.info(
            "NodeManager initialization completed in {:0.2f} sec.".format(init_time)
        )
        app_log.info(
            "frozen edge: {}, {} from open".format(self.frozen_edge, self.from_open)
        )

    def _poll(self):
        """
        Will ask the node for the new blocks/tx since last known state and run through filters
        :return:
        """
        # app_log.info("Polling {}".format(self.frozen_edge))
        # Lock to prevent polling while another command is going on
        with self._query_lock:
            if self._client_process is None:
                self._create_client_process()
            if self._client_process is None:
                app_log.error("Unable to create client process")
                return
            self._client_process.sendline("")
            index = self._client_process.expect([TIMEOUT, RE_STATUS, EOF])
            if index == 1:
                self.frozen_edge = int(
                    self._client_process.match.groups()[0].decode("utf-8")
                )
                self.from_open = int(self._client_process.match.groups()[1].decode("utf-8"))
            else:
                self._client_gone()
        app_log.info(
            "frozen edge: {}, {} from open".format(self.frozen_edge, self.from_open)
        )

    def _balance(self, address: str ) -> str:
        with self._query_lock:
            try:
                balance = "-1"
                balances = {}
                block = 0
                if self._client_process is None:
                    self._create_client_process()
                if self._client_process is None:
                    app_log.error("Unable to create client process")
                    return balance
                try:
                    # make suree nothing is left in buffer.
                    self._client_process.read_nonblocking(1000000000, timeout=0.1)
                except:
                    pass
                self._client_process.sendline("BL")
                index = self._client_process.expect([TIMEOUT, "wallet ID or prefix:"])
                if index == 1:
                    self._client_process.sendline(address)
                    # index = self._client_process.expect([TIMEOUT, "╠"])  # end of table header
                    index = self._client_process.expect([TIMEOUT, "balance"])  # end of table header
                    # print("saw balance ", self._client_process.before, self._client_process.after)
                    if index == 0:
                        app_log.error("timeout")
                        return balance
                    while True:
                        print("loop")
                        index = self._client_process.expect([TIMEOUT, RE_BALANCE, RE_STATUS, EOF])  # balance line or last line
                        if index == 0:
                            app_log.error("timeout")
                            return balance
                        elif index == 1:  # balance line - todo utf decode
                            #app_log.error("Balance line")
                            # print(self._client_process.match.groups())
                            address = re.sub(r'[^0123456789abcdef]', '', self._client_process.match.groups()[1].decode("utf-8").lower())
                            balances[address] = self._client_process.match.groups()[3].decode("utf-8")
                            block = self._client_process.match.groups()[0].decode("utf-8")
                        elif index == 2:
                            #app_log.error("Status line")
                            # print("saw status ", self._client_process.before, self._client_process.after)
                            self.frozen_edge = int(
                                self._client_process.match.groups()[0].decode("utf-8")
                            )
                            self.from_open = int(self._client_process.match.groups()[1].decode("utf-8"))
                            break  # last line, satus
                        else:  # eof
                            app_log.error("Client gone")
                            self._client_gone()
                            return balance
                else:
                    app_log.error("timeout 2")
                    self._client_gone()
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        # print(block)
        # print(balances)

        balance = balances.get(address, -1)
        app_log.info(
            "balance: {}, {}".format(address, balance)
        )
        return balance

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

    async def stop(self, *args, **kwargs):
        """Clean stop the server"""
        app_log.info("Stopping Server")
        # self.connection.close()
        # Close possible open files and processes
        if not self._client_process is None:
            self._client_process.sendline('x')
            app_log.info("Waiting for Nyzo client to stop...")
            self._client_process.expect(EOF)
            app_log.info("Nyzo client stopped")
        # Signal possible threads to terminate and wait.
        self.stop_event.set()
        # self.watchdog_thread.join() It's a daemon thread, no need to wait,
        # it can take up to 10 sec because of the sleep()
        ioloop = IOLoop.instance()
        # ioloop.add_callback(ioloop.stop)  # stops before answering the client
        ioloop.add_timeout(time() + 0.1, ioloop.stop)
        # NOT So simple. Have to signal tornado app to close (and not leave the port open) see
        # https://stackoverflow.com/questions/5375220/how-do-i-stop-tornado-web-server
        # https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
        # sys.exit()
        return True

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
            # bitcoind alike - TODO: complete
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

    async def getbalancebyaddress(self, *args, **kwargs):
        """
        Returns the total balance of a specific address
        This is an extra command, not included in default bitcoin json-rpc
        """
        try:
            minconf = 1
            if len(args) > 2:
                minconf = args[2]
            if minconf < 1:
                minconf = 1
            address = args[1]
            balance = self._balance(address)
            return balance
        except Exception as e:
            return {"version": self.config.version, "error": str(e)}
