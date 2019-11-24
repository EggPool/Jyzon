#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A Mockup script for NyzoVerifier client

(c) EggdraSyl - EggPool.net

"""

import random
import sys
import re
from time import sleep
from threading import Thread
from nyzostrings.nyzostringencoder import NyzoStringEncoder
from nyzostrings.nyzostringpublicidentifier import NyzoStringPublicIdentifier

__version__ = "0.0.2"  # Mockup version


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


def command(message: str=""):
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


# TODO: Could make its way to nyzostrings
def normalize_id(address: str) -> str:
    """converts id_ to raw hex, Removes extra chars from raw hex"""
    if address.startswith("id_"):
        try:
            address = NyzoStringEncoder.decode(address).get_bytes().hex()
        except:
            address = "0000000000000000000000000000000000000000000000000000000000000000"
            print("Bad address, mapped to 000...000")
    address = re.sub(r'[^0123456789abcdef]', '', address.lower())
    return address


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
    address = normalize_id(address)
    print("wallet ID or prefix after normalization: {}".format(address))
    nyzo_string = NyzoStringPublicIdentifier.from_hex(address)
    id_ = NyzoStringEncoder.encode(nyzo_string)
    if address == "":
        print("please provide a wallet ID or prefix")
        return
    if address == 'ff':
        print("""╔═════════╦═════════════════════════════════════════════════════════════════════╦══════════════════════════════════════════════════════════╦═════════════════╗
║ block   ║                                                                     ║                                                          ║                 ║
║ height  ║ wallet ID                                                           ║ ID string                                                ║ balance         ║
╠═════════╬═════════════════════════════════════════════════════════════════════╬══════════════════════════════════════════════════════════╬═════════════════╣
║ 5399202 ║ ff0e597aa28012f4-cfba7ef9f1c25bf6-4ebd9bc209dfaff8-b60110f1854aa540 ║ id__8f-enoHzx1bSRZG~~w72n_qeMqM22u~M~bp14f65iHm03viaTvr5 ║ ∩1356604.936151 ║
║ 5399202 ║ ff188d0027165772-3fd521e65983f4fb-140840e6a720450e-f35494e81f80a1b1 ║ id__8f-pAg0E5CuQf.kyXCD3.fJk243DGQ153MdkCexwxa6PWCbQDtgJ ║ ∩84.885685      ║
║ 5399202 ║ ff1b27802b6cce82-436133b101a97fe3-ef3839b36c06099b-abc3f106e104d3b3 ║ id__8f-s9W0IscY2gU4RJg6Gw~fMe3DRs0p9DYM3-gsy1deRQhS9JCzp ║ ∩75.840805      ║
║ 5399202 ║ ff3d6af8305cf2f8-8dafbb56512bc4a5-52729f38f1be83ec-96b54241e00d8929 ║ id__8f-.rMxNofbWAr~ZmC4IPamitG-W-sY3Z9rTgB7x3pBGa974CD4E ║ ∩10.972408      ║
║ 5399202 ║ ff4343e18a1e0c31-db8e48484d788a91-933d824ac03d36da-81af418df9cf2af8 ║ id__8f.3g~6a7xNPUWX8i4TWzG6jfp9aN3SUUF6MgpVXRQIWmuGBhEqb ║ ∩180.734644     ║
║ 5399202 ║ ff4dfe7e7b99e3f1-45024726dc37bcc8-210266968763f34e-0c4bc57ec85e4cc8 ║ id__8f.d_EXZDvfPhg979KNVMcxy0DrnyUfRjxPbPoZ8oBR8jxGJTGwp ║ ∩37.600176      ║
║ 5399202 ║ ff538fa326122ee6-7d2c1622ea2a701b-9e1dd8fcf26e2b71-8b88b68b22afc735 ║ id__8f.jAYcD4zZDwiNn8LFHt1Lv7uA--DWItpL8KFJzI-tT4NAP1Lu. ║ ∩111.229775     ║
║ 5399202 ║ ff614fbcd5aaf1b6-e2a4aec20fc0f244-fd47d5ef1fff45e3-32b3a9461b6d041e ║ id__8f.yjZRmHM6UWHiLNx_0-Bj.h.oM7_.5WRaRHkpssggvf5pBgKN7 ║ ∩206.594460     ║
║ 5399202 ║ ff698862706afa10-88731b8a23c37605-cdf26f2f1a17a8ab-ee7ea519d78e8112 ║ id__8f.Gz69NrMFgz7cszzf3uxod-D-M6yvFH~X~GhEoAF4i0tpBIYx6 ║ ∩97.706838      ║
║ 5399202 ║ ff7f024298d5b2ed-6799302c31e97102-9829c8ec048531af-94dbc4cf739ad52e ║ id__8f._0BapTsbKqXBNb37GtgapatAJ18kPIXjsPc.RDKkL7nAyerzL ║ ∩416.309419     ║
║ 5399202 ║ ff82ccaad7b6ad58-5eb0d8707c878ff3-e94f8ab91013f153-c6f5de295e1fd8d3 ║ id__8f~2RaIoKHTpoI3pt7Q7A_fGjWHX41fPk-sTVzCv7.AjiQL2Ecwf ║ ∩56.073429      ║
║ 5399202 ║ ff8a6f99d1e8b3ef-40a899970cec1ff2-5924f6c6b147243c-471be6fc25770398 ║ id__8f~asXEhYbfMgazqCNRJ7_9q9fs6JktBf4tsXMNCuNep2HNoSVB- ║ ∩10.174500      ║
║ 5399202 ║ ffb5a85fcc138983-d463d5b2c4a949ed-8d06dc7a04cefb81-03eadc0bf4213605 ║ id__8f~TH5_c4WD3T6fmJJiGivUd1KPY1cZZxgfHV0MS8jp5_Y6rkcI7 ║ ∩1354.290441    ║
║ 5399202 ║ ffb7706cc9cf2f0f-abe77438d2370c57-044aea0c5cd56035-1039a7e2c3a9190b ║ id__8f~Vt6R9RQ-fH~uSed8V35t4iLFcodmxdh0XG~b3HhBbPkhjsqZK ║ ∩484.809293     ║
║ 5399202 ║ ffbb94829f67e861-e7ba24decfb45f49-5507d686d08fff84-1bfa5b8893fb52df ║ id__8f~ZC8awq~yyXZFBVJ~SoSCm1.r6S8__y1MYnWzj~TbwSUjI0_ox ║ ∩40.364892      ║
║ 5399202 ║ ffbefdf86aac750f-62964e0f080f9f44-33874a0f726c34ff-bec4f522439cce01 ║ id__8f~~_wyHI7kfpGqe3NxfESgRySFftDNS_ZZ4.i93EcW153QA7-Mx ║ ∩137.430708     ║
║ 5399202 ║ ffd476bde89b47cc-7406f60dc250e828-dff6152c2f9fb002-8414436e45f7c6ab ║ id__8f_kuIVFDSwcu0sU3t9gY2Aw.ykJbX~N0FgkgUX5.-rI.Q8FqVNH ║ ∩6432.872405    ║
║ 5399202 ║ fffabcff6162fbbf-a122e001b95630be-30624f75a708d5e3-228d64e0df27c799 ║ id__8f_YMf.ypML_Fibx0sCncbWNpB.TGNAmWQadqe3w9-vq~9M.X9ah ║ ∩449.074037     ║
╚═════════╩═════════════════════════════════════════════════════════════════════╩══════════════════════════════════════════════════════════╩═════════════════╝
""")
        return

    # TODO: here, address should be re-converted with dashes to fit the real client display
    print("""╔═════════╦═════════════════════════════════════════════════════════════════════╦══════════════════════════════════════════════════════════╦═══════════════╗
║ block   ║                                                                     ║                                                          ║               ║
║ height  ║ wallet ID                                                           ║ ID string                                                ║ balance       ║
╠═════════╬═════════════════════════════════════════════════════════════════════╬══════════════════════════════════════════════════════════╬═══════════════╣
║ {frozen} ║ {address} ║ {id_} ║ ∩1234.{rand:0000} ║
╚═════════╩═════════════════════════════════════════════════════════════════════╩══════════════════════════════════════════════════════════╩═══════════════╝
""".format(frozen=FROZEN, address=address, id_=id_, rand=random.randint(1, 1000)))



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
