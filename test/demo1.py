#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test and dev json-rpc client
"""

# http://jsonrpcclient.readthedocs.io/en/latest/api.html
import jsonrpcclient

# from jsonrpcclient.clients.http_client import HTTPClient
from jsonrpcclient.http_client import HTTPClient

jsonrpcclient.config.validate = False

# a real bitcoind server with -regtest -rpcuser=username -rpcpassword=password
# client = HTTPClient('http://username:password@127.0.0.1:18332/')

# The test jyzond.py server
client = HTTPClient("http://username:password@127.0.0.1:8444/")
# client.session.headers.update({"Content-Type": "application/json-rpc"})

# For json-rpc over SSL
# client.session.verify = '/path/to/certificate'

## AUTH ##
# Simple Auth - see http://docs.python-requests.org/en/master/user/authentication/
client.session.auth = ("username", "password")

## Misc ##
client.session.headers.update({"Connection": "close"})


## Requests ##

client.request("getinfo")
# or : client.send('{"method": "getinfo","params":[],"id":1,"jsonrpc":"2.0"}')
# WARNING: getinfo is deprecated and will be fully removed in 0.16. Projects should transition to using getblockchaininfo, getnetworkinfo, and getwalletinfo before upgrading to 0.16

# This one should be cached
# client.request('getinfo')

# Test with a random address
client.request("getbalancebyaddress", ["ff188d0027165772-3fd521e65983f4fb-140840e6a720450e-f35494e81f80a1b1"])


# client.request("stop")
## FOR REFERENCE ONLY - Wiresharked

# bitcoin-cli -regest -getinfo
"""
POST / HTTP/1.1
Host: 127.0.0.1
Connection: close
Authorization: Basic X19jb29raWVfXzpiMTYxODJmYjJmMDAzMWYyZmIyYmFmYzAxNTA4YTQ2NWI3YmY1MmFlYjU4NGVmZjk2ZGVjYTA3YjlmMDU5OGFk
>> __cookie__:b16182fb2f0031f2fb2bafc01508a465b7bf52aeb584eff96deca07b9f0598ad
Content-Length: 40

{"method":"getinfo","params":[],"id":1}
HTTP/1.1 200 OK
Content-Type: application/json
Date: Mon, 22 Jan 2018 20:23:22 GMT
Content-Length: 531
Connection: close

{"result":{"deprecation-warning":"WARNING: getinfo is deprecated and will be fully removed in 0.16. Projects should transition to using getblockchaininfo, getnetworkinfo, and getwalletinfo before upgrading to 0.16","version":150100,"protocolversion":70015,"walletversion":139900,"balance":99.99996160,"blocks":102,"timeoffset":0,"connections":0,"proxy":"","difficulty":4.656542373906925e-10,"testnet":false,"keypoololdest":1516567161,"keypoolsize":2000,"paytxfee":0.00000000,"relayfee":0.00001000,"errors":""},"error":null,"id":1}
"""
# Warning: json does not validate schema (both result and error, even if error is null)
