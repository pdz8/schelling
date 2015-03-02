#!/usr/bin/env python
import sys
import json
import requests
import sha3
from docopt import docopt


# Defaults
RPC_SERVER = "http://localhost:8080"
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8080
DEFAULT_GASPRICE = 10 ** 12
DEFAULT_STARTGAS = 10000 # ,"gas":DEFAULT_STARTGAS,"gasPrice":DEFAULT_GASPRICE


#################
## RPC methods ##
#################

# Get the balance at given address
def get_balance(addr):
	addr = prepend0x(addr)
	skeleton = {"jsonrpc":"2.0","method":"eth_balanceAt","params":[addr],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')


# Get the storage at a given address and index
def get_state(addr, index):
	addr = prepend0x(addr)
	if isinstance(index, str):
		index = prepend0x(index)
	# if not isinstance(index, str):
	# 	index = hex(index)
	skeleton = {"jsonrpc":"2.0","method":"eth_stateAt","params":[addr, index],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')


# Make transaction
def transact(recip, ethval, code, sender=None):
	recip = prepend0x(recip)
	if not isinstance(ethval, str):
		ethval = hex(ethval)
	else:
		ethval = prepend0x(ethval)
	code = prepend0x(code)
	if not sender:
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"to":recip,"code":code}],"id":1}
	else:
		sender = prepend0x(sender)
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"to":recip,"code":code,"from":sender}],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return r.text


# Make contract
def create_contract(ethval, code, sender=None):
	if not isinstance(ethval, str):
		ethval = hex(ethval)
	else:
		ethval = prepend0x(ethval)
	code = prepend0x(code)
	if not sender:
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"code":code}],"id":1}
	else:
		sender = prepend0x(sender)
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"code":code,"from":sender}],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')


# Get the coinbase of the rpc server
def get_coinbase():
	skeleton = {"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":64}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')

def set_coinbase(addr):
	addr = prepend0x(addr)
	skeleton = {"jsonrpc":"2.0","method":"eth_setCoinbase","params":[addr],"id":66}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))

def get_accounts():
	skeleton = '{"jsonrpc":"2.0","method":"eth_accounts","params":null,"id":1}'
	r = requests.post(RPC_SERVER, data=skeleton)
	return r.text


####################
## Helper methods ##
####################

# Add the 0x prefix to addresses
def prepend0x(s):
	if not s.startswith('0x'):
		s = '0x' + s
	return s

# Remove the 0x prefix from hex
def remove0x(s):
	if s.startswith('0x'):
		s = s[2:]
	return s

# Make s have 64 hex characters
def padzeros(s):
	s = remove0x(s)
	while len(s) < 64:
		s = '0' + s
	return s

# Convert to int if possible
def try_int(i):
	try:
		int(i)
		return int(i)
	except:
		return i


########################
## Formatting methods ##
########################

# Encode a function call into abi form
# Only allows uint and address types currently
def encode_abi(sig, *args):
	if '(' in sig:
		abi = sha3.sha3_256(sig).hexdigest()[:8]
	else:
		abi = prepend0x(sig)
	for arg in args:
		if isinstance(arg, str):
			abi += padzeros(arg)
		elif isinstance(arg, int):
			abi += padzeros(hex(arg))
	return prepend0x(abi)



# docopt is awesome
usage_string = \
"""
Ethereum RPC

Usage:
  ethrpc encode_abi <sig> [<params>...]
  ethrpc get_balance <addr>
  ethrpc get_state <addr> <index>
  ethrpc transact <recip> <ethval> <code> [<sender>]
  ethrpc create_contract <ethval> <code> [<sender>]
  ethrpc get_accounts

Options:
  -h --help
  -H --host=<host>
  -p --port=<port>
"""
if __name__ == "__main__":
	args = docopt(usage_string)

	# Initialize contract
	host = args.get('--host') or DEFAULT_HOST
	port = int(args.get('--port') or DEFAULT_PORT)
	RPC_SERVER = "http://{0}:{1}".format(host, str(port))

	# Switch statment
	sender = args.get("<sender>") or None
	if args['encode_abi']:
		params = args["<params>"]
		for i in range(len(params)):
			params[i] = try_int(params[i])
		r = encode_abi(args["<sig>"], *params)
		sys.stdout.write(r)
	elif args['get_balance']:
		r = get_balance(args["<addr>"])
		sys.stdout.write(r)
	elif args['get_state']:
		r = get_state(args["<addr>"], try_int(args["<index>"]))
		sys.stdout.write(r)
	elif args['transact']:
		r = transact(
			args["<recip>"], try_int(args["<ethval>"]),
			args["<code>"], sender=sender)
		sys.stdout.write(r)
	elif args['create_contract']:
		r = create_contract(
			try_int(args["<ethval>"]), args["<code>"], sender=sender)
		sys.stdout.write(r)
	elif args['get_accounts']:
		r = get_accounts()
		sys.stdout.write(r)


