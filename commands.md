# Jyzon json-rpc commands and formats

I try to mimick or be as close as bitcoind commands as possible.    
Given the conceptual differences between Nyzo and BTC, this is not always possible, so the differences also will be highlighted.

## Bitcoin client API Command List

Here is the original list from https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
A more up to date reference is here: https://bitcoin.org/en/developer-reference

I'll edit along the way with what is supported or not (yet)

This list and comments are WIP.

## API Versions
- 0.1a:  getinfo
- 0.1b:  getbalancebyaddress

## Accounts

An account roughly represents a user. An account may hold one or several addresses.  
You can also think of an account as a group of addresses.
An account is either an empty string (default account) or 2-128 characters long, and may only contains the Base64 Character set.  
So, a numeric ID (in decimal or Hex form) is also ok.

## Implemented

* getinfo - Returns an object containing various state info.  
  Compatible, plus extra info.
  
* getbalancebyaddress  -  (nyzo address, raw or id_) (minconf=1)  -  Returns the total balance of the given address, with minconf confirmations.    
  minconf value is 1 and has no impact.
  
  
## Implemented, need further work to be more bitcoind compatible

TODO

## To be Implemented Specific Jyzond commands

These commands are not known nor used by bitcoind

* reindexwallet - force a rebuild of the indexed index {address: account}  

* rescan - Scan whole blockchain for all accounts, addresses and updates all balances.  
  Update: No need to, we ask the node the get updated balances, no need to cache and risk some divergence.

* getblocksince -  (block) - Returns the full blocks (with all transactions) following a given block_height  
  Returns at most 10 blocks (the most recent ones)  
  Used by the json-rpc server to poll and be notified of tx and new blocks.
  
* getaddresssince - (block) (minconf) (nyzo address) - Returns the transactions matching the given address, following a given block_height, with at least minconf confirmations.    
  Returns at most info from 720 blocks (the older ones)  
  Used by the json-rpc server to poll and be notified of tx and new blocks.

## Working on





## Postponing

See new commands:

* getblockchaininfo https://bitcoin.org/en/developer-reference#getblockchaininfo  
  Will need some adjustments, see what is coherent in the data
* getnetworkinfo https://bitcoin.org/en/developer-reference#getnetworkinfo


## Help Appreciated

The following commands are self contained and should be OK to implement in a safe a independent way.  
I can do it, but it's always nice not to be alone :)

TODO

The more the project move forward, the more difficult it is to give small tasks for beginners.  
So I won't add more here, but you can look at the code, and if you understand and feel comfortable with it, then pick a function from "To be implemented" and give it a try.  
Tell me via an issue so I know you're working on it.


## To be implemented

* help  -  (command)  -  List commands, or get help for a command.
* Wallet encryption   
* stop  -  Stop Jyzond server.
* getconnectioncount  -   * Returns the number of connections to other nodes. 
* listreceivedbyaccount  -  (minconf=1) (includeempty=false)  -  Returns an array of objects containing:   
  "account" : the account of the receiving addresses, "amount" : total amount received by addresses with this account, "confirmations": number of confirmations of the most recent transaction included

* listreceivedbyaddress  -  (minconf=1) (includeempty=false)  -  Returns an array of objects containing:  
  "address" : receiving address, "account" : the account of the receiving address, "amount" : total amount received by the address, "confirmations": number of confirmations of the most recent transaction included.  
  To get a list of accounts on the system, execute listreceivedbyaddress 0 true
  


## TBI, but needs a verifier side indexer

* listsinceblock  -  (blockhash) (target-confirmations)  -  Get all transactions affecting the wallet in blocks since block (blockhash), or all transactions if omitted. (target-confirmations) intentionally does not affect the list of returned transactions, but only affects the returned "lastblock" value.  
  https://bitcoin.org/en/developer-reference#listsinceblock 
  **WARNING** Answers right now, but with mockup data
* listtransactions  -  (account) (count=10) (from=0)  -  Returns up to (count) most recent transactions skipping the first (from) transactions for account (account). If (account) not provided it'll return recent transactions from all accounts.


## Undecided

* getaddednodeinfo  -  (dns) (node)  -  version 0.8 Returns information about the given added node, or all added nodes

* createmultisig  -  (nrequired) &lt;'("key,"key")'&gt;  -  Creates a multi-signature address and returns a json object  | 
* addmultisigaddress  -  (nrequired) &lt;'("key","key")'&gt; (account)  -  Add a nrequired-to-sign multisignature address to the wallet. Each key is a bitcoin address or hex-encoded public key. If (account) is specified, assign address to (account). Returns a string containing the address. 

Not sure these are useful (can use dedicated calls)
* sendrawtransaction  -  (hexstring)  -  version 0.7 Submits raw transaction (serialized, hex-encoded) to local node and network. 
* decoderawtransaction  -  (hex string="")  -  version 0.7 Produces a human-readable JSON object for a raw transaction.



## Won't implement

* keypoolrefill  -   * Fills the keypool, requires wallet passphrase to be set. 
* setaccount  -  (bitcoinaddress) (account)  -  Sets the account associated with the given address. Assigning address that is already assigned to the same account will create a new address associated with that account.
  Deprecated 
* listaddressgroupings  -   * version 0.7 Returns all addresses in the wallet and info used for coincontrol. 
  https://bitcoin.org/en/developer-reference#listaddressgroupings
* move  -  (fromaccount) (toaccount) (amount) (minconf=1) (comment)  -  Move from one account in your wallet to another 
* getmemorypool  -  (data)  -  Replaced in v0.7.0 with getblocktemplate, submitblock, getrawmempool 
* sendmany  -  (fromaccount) {address:amount,...} (minconf=1) (comment)  -  amounts are double-precision floating point numbers  
  Nyzo does not support one to many transactions. Will be converted to many transactions, and return a list of transaction id.  
  Deprecated for bitcoin, so won't implement.


## These commands may have no sense in the Nyzo context.

* gettxout  -  (txid) (n) (includemempool=true)  -  Returns details about an unspent transaction output (UTXO) 
* gettxoutsetinfo  -   * Returns statistics about the unspent transaction output (UTXO) set 

* setgenerate  -  (generate) (genproclimit)  -  (generate) is true or false to turn generation on or off.Generation is limited to (genproclimit) processors, -1 is unlimited. 
* getgenerate  -   * Returns true or false whether bitcoind is currently generating hashes 
* gethashespersec  -   * Returns a recent hashes per second performance measurement while generating. 
* invalidateblock  -  (hash)  -  Permanently marks a block as invalid, as if it violated a consensus rule.
* settxfee  -  (amount)  -  (amount) is a real and is rounded to the nearest 0.00000001 
* getblocktemplate  -  (params)  -  Returns data needed to construct a block to work on. See  BIP_0022 for more info on params.
* getmininginfo  -   * Returns an object containing mining-related information: blocks, currentblocksize,currentblocktx, difficulty,errors,generate,genproclimit,hashespersec,pooledtx, testnet
* submitblock  -  (hex data="") (optional-params-obj)  -  Attempts to submit new block to network. 
* getrawchangeaddress  -  (account) * version 0.9 Returns a new Bitcoin address, for receiving change. This is for use with raw transactions, NOT normal use. 
* getwork  -  (data)  -  If (data) is not specified, returns formatted hash data to work on:, "midstate"&nbsp;: precomputed hash state after hashing the first half of the data,  "data"&nbsp;: block data,  "hash1"&nbsp;: formatted hash buffer for second hash,  "target"&nbsp;: little endian hash target, If (data) is specified, tries to solve the block and returns true if it was successful.
* listlockunspent  -   * version 0.8 Returns list of temporarily unspendable outputs
* lockunspent  -  (unlock?) (array-of-objects)  -  version 0.8 Updates list of temporarily unspendable outputs
* listunspent  -  (minconf=1) (maxconf=999999)  -  version 0.7 Returns array of unspent transaction inputs in the wallet. 
* clearbanned - The clearbanned RPC clears list of banned nodes.
* addnode  -  (node) (add remove="" onetry="")  -  version 0.8 Attempts add or remove (node) from the addnode list or try a connection to (node) once.  
* getrawmempool  -   * Returns all transaction ids in memory pool 
* getmempoolinfo  -  returns information about the node’s current transaction memory pool.  
  https://bitcoin.org/en/developer-reference#getmempoolinfo
 
