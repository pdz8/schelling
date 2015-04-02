#!/usr/bin/env python
import sys
import json
import requests
import sha3
from docopt import docopt
from ethutils import prepend0x, remove0x, padzeros, try_int, removeL


# Defaults
RPC_SERVER = "http://localhost:8080"
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8080
DEFAULT_GASPRICE = 10 ** 12
DEFAULT_STARTGAS = 10000 # ,"gas":DEFAULT_STARTGAS,"gasPrice":DEFAULT_GASPRICE
CONSTRUCTOR_SIG = 'constructor_sig'


#################
## RPC methods ##
#################

class EthRpc():
	def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, poc=8):
		self.server = "http://{0}:{1}".format(host, str(port))
		self.poc = poc

	# Do a json request
	def make_request(self, skeleton):
		r = requests.post(self.server, data=json.dumps(skeleton))
		return json.loads(r.text)

	# Get the balance at given address
	def get_balance(self, addr):
		addr = prepend0x(addr)
		skeleton = {"jsonrpc":"2.0","method":"eth_balanceAt","params":[addr],"id":1}
		if self.poc == 9:
			skeleton = {"jsonrpc":"2.0","method":"eth_getBalance","params":[addr,"latest"],"id":1}
		h = self.make_request(skeleton)['result'].encode('ascii','ignore')
		return int(h, 16)

	# Get full storage state
	def get_storage(self, addr):
		addr = prepend0x(addr)
		skeleton = {"jsonrpc":"2.0","method":"eth_storageAt","params":[addr],"id":1}
		if self.poc == 9:
			skeleton = {"jsonrpc":"2.0","method":"eth_getStorage","params":[addr,"latest"],"id":1}
		store = self.make_request(skeleton)['result']
		retval = {}
		for k in store:
			retval[k.encode('ascii','ignore')] = store[k].encode('ascii','ignore')
		return retval

	# Get the storage at a given address and index
	def get_index(self, addr, index):
		addr = prepend0x(addr)
		if isinstance(index, str):
			index = prepend0x(index)
		if not isinstance(index, str):
			index = hex(index)
		skeleton = {"jsonrpc":"2.0","method":"eth_stateAt","params":[addr,index],"id":1}
		if self.poc == 9:
			skeleton = {"jsonrpc":"2.0","method":"eth_getStorageAt","params":[addr,index,"latest"],"id":1}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	# Do a simple call (getters)
	def call(self, addr, sig, args, data=None):
		addr = prepend0x(addr)
		if data:
			data = prepend0x(data)
		else:
			data = encode_abi(sig, args)
		skeleton = {"jsonrpc":"2.0","method":"eth_call","params":[{"to":addr,"data":data}],"id":1}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	# Make transaction
	def transact(self, recip, ethval, sig, args, data=None, sender=None):

		# Format input
		recip = prepend0x(recip)
		if not isinstance(ethval, str):
			ethval = hex(ethval)
		else:
			ethval = prepend0x(ethval)
		ethval = removeL(ethval)
		if data:
			data = prepend0x(data)
		elif sig:
			data = encode_abi(sig, args)
		else:
			data = ""

		# Make call
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"to":recip,"data":data}],"id":1}
		if self.poc == 9:
			skeleton = {"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":ethval,"to":recip,"data":data}],"id":1}
		if sender:
			sender = prepend0x(sender)
			skeleton["params"][0]["from"] = sender
		return self.make_request(skeleton)


	# Make contract
	def create_contract(self, ethval, code, args=[], sender=None):
		
		# Format inputs
		if not isinstance(ethval, str):
			ethval = hex(ethval)
		else:
			ethval = prepend0x(ethval)
		ethval = removeL(ethval)
		code = prepend0x(code)
		if args:
			code += encode_abi('', args)[2:]

		# Format and send request
		skeleton = {"jsonrpc":"2.0","method":"eth_transact","params":[{"value":ethval,"code":code}],"id":1}
		if self.poc == 9:
			skeleton = {"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":ethval,"code":code}],"id":1}
		if sender:
			sender = prepend0x(sender)
			skeleton["params"][0]["from"] = sender
		return self.make_request(skeleton)['result'].encode('ascii','ignore')


	# Get the coinbase of the rpc server
	def get_coinbase(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":64}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	def set_coinbase(self, addr):
		addr = prepend0x(addr)
		skeleton = {"jsonrpc":"2.0","method":"eth_setCoinbase","params":[addr],"id":66}
		self.make_request(skeleton)

	def get_accounts(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}
		accs = self.make_request(skeleton)['result']
		for i in range(len(accs)):
			accs[i] = accs[i].encode('ascii','ignore')
		return accs

	def get_coinbase(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":64}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')



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


##########################
## Contract convenience ##
##########################

class Contract():
	def __init__(self, abi, c_addr=None, rpc=None):
		self.c_addr = c_addr
		self.abi = abi
		self.input_types = {}
		self.input_names = {}
		self.output_types = {}
		self.output_names = {}
		for f in abi:
			fname = f['name']
			self.input_types[fname] = [a['type'] for a in f['inputs']]
			self.input_names[fname] = [a['name'] for a in f['inputs']]
			self.output_types[fname] = [a['type'] for a in f['outputs']]
			self.output_names[fname] = [a['name'] for a in f['outputs']]
		self.rpc = rpc

	# Compute the abi data (encode_abi)
	@classmethod
	def abi_to_hex(cls, input_types, fname, args):

		# Create hash of signature
		sig = fname + '('
		types = input_types[fname]
		sig += ','.join(types)
		sig += ')'
		retval = sha3.sha3_256(sig).hexdigest()[:8]

		# Append arguments
		for i in range(len(types)):
			typ = types[i]
			arg = args[i]
			if typ in ['uint256','hash256','address']:
				if isinstance(arg, str):
					retval += padzeros(arg)
				elif isinstance(arg, int):
					retval += padzeros(removeL(hex(arg)))
			elif typ == 'bool':
				if arg:
					retval += padzeros('1')
				else:
					retval += padzeros('0')
			elif typ.startswith('string'):
				retval += padzeros(arg.encode('hex'))

		# Exit
		return retval

	# Create a contract
	@classmethod
	def create(cls, code, args, abi, rpc, sender=None, ethval=0):
		c = cls(abi, rpc=rpc)
		if args:
			if not CONSTRUCTOR_SIG in c.input_types:
				return None
			code += cls.abi_to_hex(c.input_types, CONSTRUCTOR_SIG, args)[8:]
		c.c_addr = rpc.create_contract(ethval, code, args=[], sender=sender)
		return c

	# Make call
	def call(self, fname, args, c_addr=None):
		if not c_addr:
			c_addr = self.c_addr
		data = Contract.abi_to_hex(self.input_types, fname, args)
		return self.rpc.call(c_addr, None, None, data=data)

	# Make transaction
	def transact(self, fname, args, ethval=0, sender=None, c_addr=None):
		if not c_addr:
			c_addr = self.c_addr
		data = Contract.abi_to_hex(self.input_types, fname, args)
		return self.rpc.transact(
			c_addr, ethval, None, None, data=data, sender=sender)



#########
## CLI ##
#########

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
	rpc = EthRpc(host, port)

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
		r = rpc.get_balance(args["<addr>"])
		sys.stdout.write(str(r))
	elif args['get_storage']:
		r = rpc.get_storage(args["<addr>"])
		sys.stdout.write(str(r))
	elif args['call']:
		r = rpc.call(args["<recip>"], sig, params, data=data)
		sys.stdout.write(str(r))
	elif args['get_index']:
		r = rpc.get_index(args["<addr>"], try_int(args["<index>"]))
		sys.stdout.write(str(r))
	elif args['transact']:
		r = rpc.transact(
			args["<recip>"], try_int(args["<ethval>"]),
			sig, params, data=data, sender=sender)
		sys.stdout.write(str(r))
	elif args['create_contract']:
		r = rpc.create_contract(
			try_int(args["<ethval>"]),
			args["<code>"],
			args=params,
			sender=sender)
		sys.stdout.write(str(r))
	elif args['get_accounts']:
		r = rpc.get_accounts()
		sys.stdout.write(str(r))
	elif args['get_coinbase']:
		r = rpc.get_coinbase()
		sys.stdout.write(str(r))



# vim: set noexpandtab:
# vim: set tabstop=4:
# vim: set shiftwidth=4:

