#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A Mockup script for NyzoVerifier client

(c) EggdraSyl - EggPool.net

"""

import random
import sys
from time import sleep
from threading import Thread

__version__ = "0.0.1"  # Mockup veersion


VERSION = 552  # Impersonating client version
START = 10000

FROZEN = START
FROM_OPEN = 0

SHORTCUTS = {
    "BL": "balance",
    "ST": "send",
    "NSS": "seedString",
    "NIS": "idString",
    "PRC": "createPrefill",
    "PRS": "sendPrefill",
    "CTS": "cycleSend",
    "CTL": "cycleList",
    "CTX": "cycleSign",
    "X": "exit",
}

NO_HELP = False
STOPPING = False

def start():
    print(
        """*** setting run mode of Client for version {version} ***
╔══════════════════════════╗
║ Nyzo client, version {version} ║
╚══════════════════════════╝
starting client data manager
added IP 51.15.211.156 to whitelist
added IP 188.165.250.78 to whitelist
added IP 51.15.86.249 to whitelist
added IP 34.218.12.230 to whitelist
added IP 109.190.174.238 to whitelist
added IP 78.209.40.4 to whitelist
NodeManager initialization: loaded 14378 nodes into map
set frozen edge to {frozen} in individual loading
completed BlockManager initialization
entering frozen-edge consensus process because open edge, {frozen}, is {from_open} past frozen edge, {frozen} and cycleComplete=true
sending Bootstrap request to [TrustedEntryPoint: host=verifier0.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier1.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier2.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier3.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier4.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier5.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier6.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier7.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier8.nyzo.co, port=9444]
sending Bootstrap request to [TrustedEntryPoint: host=verifier9.nyzo.co, port=9444]
Bootstrap response is null
Bootstrap response is null
Bootstrap response is null
Bootstrap response is null
Bootstrap response is null
consensus bootstrap response: [BootstrapResponseV2(frozenEdgeHeight=5377021,frozenEdgeHash=bc...4c,cycleVerifiers=1560]
local frozen edge: {frozen}, consensus frozen edge: {frozen}, fetch required (not-in-cycle): true, fetch required (in-cycle): false
fetching block based on bootstrap response
trying to fetch block for height {frozen}
NicknameManager.mapLimitingThreshold=2000
received response for block fetch""".format(
            version=VERSION, frozen=FROZEN, from_open=FROM_OPEN
        )
    )


def command(message=""):
    global NO_HELP
    help = """╔═════════╦═══════════════╦════════════════════════════════════════╗
║ short   ║ full          ║                                        ║
║ command ║ command       ║ description                            ║
╠═════════╬═══════════════╬════════════════════════════════════════╣
║ BL      ║ balance       ║ display wallet balances                ║
║ ST      ║ send          ║ send a standard transaction            ║
║ NSS     ║ seedString    ║ create Nyzo strings for a private seed ║
║ NIS     ║ idString      ║ create Nyzo strings for a public ID    ║
║ PRC     ║ createPrefill ║ create a Nyzo prefilled-data string    ║
║ PRS     ║ sendPrefill   ║ send a prefilled-data transaction      ║
║ CTS     ║ cycleSend     ║ send a cycle transaction               ║
║ CTL     ║ cycleList     ║ list cycle transactions                ║
║ CTX     ║ cycleSign     ║ sign a cycle transaction               ║
║ X       ║ exit          ║ exit Nyzo client                       ║
╚═════════╩═══════════════╩════════════════════════════════════════╝"""
    if NO_HELP:
        NO_HELP = False
    else:
        print(help)
    print(
        """{message}frozen edge: {frozen}, {from_open} from open""".format(
            frozen=FROZEN, from_open=FROM_OPEN, message=message
        )
    )


def error():
    message = """Your selection was not recognized.
Please choose an option from the above commands.
You may type either the short command or the full command.
"""
    command(message=message)
    process_command()


def no_help():
    """Don't display full command help at next command prompt"""
    global NO_HELP
    NO_HELP = True


def beat():
    """"background thread, simulates network moving"""
    global FROZEN
    global FROM_OPEN
    issues = [1, 2, 3]  # move up 1, network moved up alone, we catched up one
    weights = [5, 3, 1]
    while not STOPPING:
        issue = random.choices(issues, weights=weights, k=1)[0]
        if issue == 1:
            FROZEN += 1
        elif issue == 2:
            FROM_OPEN += 1
        else:
            FROM_OPEN = max(0, FROM_OPEN - 1)
        for i in range(10):
            if not STOPPING:
                sleep(0.5)


"""
client commands are mapped to cmd_ methods thereafter.
"""


def cmd_exit():
    global STOPPING
    print(
        """╔══════════════════════════════════════╗
║ Thank you for using the Nyzo client! ║
╚══════════════════════════════════════╝
termination requested"""
    )
    STOPPING = True
    sys.exit()


def cmd_balance():
    no_help()
    address = input("wallet ID or prefix: ").strip()
    address = address.replace("-","")
    print("wallet ID or prefix after normalization: {}".format(address))
    if address == "":
        print("please provide a wallet ID or prefix")
        return
    # TODO: detect hexa or id_
    print("""╔═════════╦═════════════════════════════════════════════════════════════════════╦══════════════════════════════════════════════════════════╦═══════════════╗
║ block   ║                                                                     ║                                                          ║               ║
║ height  ║ wallet ID                                                           ║ ID string                                                ║ balance       ║
╠═════════╬═════════════════════════════════════════════════════════════════════╬══════════════════════════════════════════════════════════╬═══════════════╣
║ {frozen} ║ {address} ║ id__TODO ║ ∩1234.{rand:0000} ║
╚═════════╩═════════════════════════════════════════════════════════════════════╩══════════════════════════════════════════════════════════╩═══════════════╝
""".format(frozen=FROZEN, address=address, rand=random.randint(1, 1000)))



def cmd_cycleList():
    key = input(
        "in-cycle verifier key (leave empty to list locally stored transactions): "
    ).strip()
    no_help()
    if key == "":
        print(
            """╔═════════════════════════════════╗
║ no cycle transactions available ║
╚═════════════════════════════════╝"""
        )
    else:
        print(
            """querying node abcd...1234
╔═══════╦══════════════════════════════════════════════════════════╦══════════════════════════════════════════════════════════╦═══════════╦═════════╦══════════════╗
║ index ║ initiator                                                ║ receiver                                                 ║ amount    ║ block   ║ # signatures ║
╠═══════╬══════════════════════════════════════════════════════════╬══════════════════════════════════════════════════════════╬═══════════╬═════════╬══════════════╣
║ 0     ║ id__8cdasPC2QVZ13iG42RWhp47gow9SsIXZgp0Aga59oEITG2X-M7Ur ║ id__87RkKJa.xPsBgb2DI_JJvdQTT_UH5YIFPHD.hrNg0o~u0EIsZG2X ║ ∩1.000000 ║ 5400000 ║ 267          ║
╚═══════╩══════════════════════════════════════════════════════════╩══════════════════════════════════════════════════════════╩═══════════╩═════════╩══════════════╝
"""
        )


def process_command():
    command = input("command: ").strip()
    if command.upper() in SHORTCUTS:
        command = SHORTCUTS[command.upper()]
    if command == "":
        return
    command = "cmd_{}".format(command)
    if command not in globals():
        error()
        return
    globals()[command]()


if __name__ == "__main__":
    start()
    t = Thread(target=beat)
    t.start()
    while True:
        command()
        process_command()
