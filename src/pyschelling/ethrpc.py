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
	# skeleton = {"jsonrpc":"2.0","method":"eth_getBalance","params":[addr,"-0x1"],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	h = json.loads(r.text)['result'].encode('ascii','ignore')
	return int(h, 16)

# Get full storage state
def get_storage(addr):
	addr = prepend0x(addr)
	skeleton = {"jsonrpc":"2.0","method":"eth_storageAt","params":[addr],"id":1}
	# skeleton = {"jsonrpc":"2.0","method":"eth_getStorage","params":[addr,"-0x1"],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	store = json.loads(r.text)['result']
	retval = {}
	for k in store:
		retval[k.encode('ascii','ignore')] = store[k].encode('ascii','ignore')
	return retval

# Get the storage at a given address and index
def get_index(addr, index):
	addr = prepend0x(addr)
	if isinstance(index, str):
		index = prepend0x(index)
	if not isinstance(index, str):
		index = hex(index)
	skeleton = {"jsonrpc":"2.0","method":"eth_stateAt","params":[addr,index],"id":1}
	# skeleton = {"jsonrpc":"2.0","method":"eth_getStorageAt","params":[addr,index,"-0x1"],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')

# Do a simple call (getters)
def call(addr, sig, args, data=None):
	addr = prepend0x(addr)
	if data:
		data = prepend0x(data)
	else:
		data = encode_abi(sig, args)
	skeleton = {"jsonrpc":"2.0","method":"eth_call","params":[{"to":addr,"data":data}],"id":1}
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)['result'].encode('ascii','ignore')

# Make transaction
def transact(recip, ethval, sig, args, data=None, sender=None):

	# Format input
	recip = prepend0x(recip)
	if not isinstance(ethval, str):
		ethval = hex(ethval)
	else:
		ethval = prepend0x(ethval)
	if data:
		data = prepend0x(data)
	elif sig:
		data = encode_abi(sig, args)
	else:
		data = ""

	# Make call
	skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"to":recip,"data":data}],"id":1}
	# skeleton = {"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":ethval,"to":recip,"data":data}],"id":1}
	if sender:
		sender = prepend0x(sender)
		skeleton["params"][0]["from"] = sender
	r = requests.post(RPC_SERVER, data=json.dumps(skeleton))
	return json.loads(r.text)


# Make contract
def create_contract(ethval, code, args=[], sender=None):
	
	# Format inputs
	if not isinstance(ethval, str):
		ethval = hex(ethval)
	else:
		ethval = prepend0x(ethval)
	code = prepend0x(code)
	if args:
		code += encode_abi('', args)[2:]

	# Format and send request
	skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"code":code}],"id":1}
	if sender:
		sender = prepend0x(sender)
		skeleton["params"][0]["from"] = sender
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
	skeleton = '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}'
	r = requests.post(RPC_SERVER, data=skeleton)
	accs = json.loads(r.text)['result']
	for i in range(len(accs)):
		accs[i] = accs[i].encode('ascii','ignore')
	return accs

def get_coinbase():
	skeleton = '{"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":1}'
	r = requests.post(RPC_SERVER, data=skeleton)
	return json.loads(r.text)['result'].encode('ascii','ignore')


####################
## Helper methods ##
####################

# Add the 0x prefix to addresses
def prepend0x(s):
	if not s:
		return '0x0'
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
def encode_abi(sig, args=[]):
	if '(' in sig:
		abi = sha3.sha3_256(sig).hexdigest()[:8]
	else:
		abi = prepend0x(sig) # assume already hashed
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
  ethrpc get_storage <addr>
  ethrpc get_index <addr> <index>
  ethrpc call <recip> <sig> [<params>...]
  ethrpc transact <recip> <ethval> [<sig> [<params>...]]
  ethrpc create_contract <ethval> <code> [<params>...]
  ethrpc get_accounts
  ethrpc get_coinbase

Options:
  -h --help
  -H --host=<host>
  -p --port=<port>
  -s --sender=<sender>
  -d --data=<data>
"""
if __name__ == "__main__":
	args = docopt(usage_string)

	# Initialize contract
	host = args.get('--host') or DEFAULT_HOST
	port = int(args.get('--port') or DEFAULT_PORT)
	RPC_SERVER = "http://{0}:{1}".format(host, str(port))

	# Get optional and common args
	sender = args.get("--sender") or None
	data = args.get("--data") or None
	params = args.get("<params>") or []
	if params:
		for i in range(len(params)):
			params[i] = try_int(params[i])
	sig = args.get("<sig>") or ""

	# Switch statment
	if args['encode_abi']:
		r = encode_abi(sig, params)
		sys.stdout.write(str(r))
	elif args['get_balance']:
		r = get_balance(args["<addr>"])
		sys.stdout.write(str(r))
	elif args['get_storage']:
		r = get_storage(args["<addr>"])
		sys.stdout.write(str(r))
	elif args['call']:
		r = call(args["<recip>"], sig, params, data=data)
		sys.stdout.write(str(r))
	elif args['get_index']:
		r = get_index(args["<addr>"], try_int(args["<index>"]))
		sys.stdout.write(str(r))
	elif args['transact']:
		r = transact(
			args["<recip>"], try_int(args["<ethval>"]),
			sig, params, data=data, sender=sender)
		sys.stdout.write(str(r))
	elif args['create_contract']:
		r = create_contract(
			try_int(args["<ethval>"]),
			args["<code>"],
			args=params,
			sender=sender)
		sys.stdout.write(str(r))
	elif args['get_accounts']:
		r = get_accounts()
		sys.stdout.write(str(r))
	elif args['get_coinbase']:
		r = get_coinbase()
		sys.stdout.write(str(r))



# vim: set noexpandtab:
# vim: set tabstop=4:
# vim: set shiftwidth=4:

