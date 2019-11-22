# Jyzon
Jyzon is a json-rpc interface to a Nyzo verifier/client, allowing easy access to core functions for GUIs: Wallets, Cycle transactions...

## Goals

- Be as close as possible to a bitdcoind rpc server
- Safe enough to be used IRL
- Lightweight and easy to install
- Middleware for easing GUI Tools development like wallets and voting helpers.

## Architecture

- Json-rpc server
- local interface to a Nyzo verifier and nyzo client
- Translates, converts, enqueues the various requests

## Future options

- Add a websocket server
- Allow for plugins and events depending on transaction rules, like alert when receiving Nyzos or on new cycle transactions.


## Changelog

0.0.2: Mockup app
0.0.1: Initial commit, scaffold
