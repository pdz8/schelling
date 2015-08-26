#!/usr/bin/env python
import sys
import json
import requests
import sha3
from docopt import docopt
from ethutils import prepend0x, remove0x, padzeros, try_int, removeL
import ethutils as eu


# Defaults
RPC_SERVER = "http://localhost:8545"
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8545
DEFAULT_GASPRICE = 10 ** 12
DEFAULT_STARTGAS = 10000 # ,"gas":DEFAULT_STARTGAS,"gasPrice":DEFAULT_GASPRICE
CONSTRUCTOR_SIG = 'constructor_sig'


#################
## RPC methods ##
#################

class EthRpc():
	def __init__(self,
			host=DEFAULT_HOST,
			port=DEFAULT_PORT,
			version=0.8):
		self.server = "http://{0}:{1}".format(host, str(port))
		self.version = version

	# Do a json request
	def make_request(self, skeleton):
		r = requests.post(self.server, data=json.dumps(skeleton))
		return json.loads(r.text)

	# Get the client version
	def get_version(self):
		skeleton = {"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":67}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	# Get the current block number (useful for confirmations)
	def get_block_number(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83}
		return self.make_request(skeleton)['result']

	# Get the balance at given address
	def get_balance(self, addr, hex_output=False):
		addr = prepend0x(addr)
		skeleton = {"jsonrpc":"2.0","method":"eth_getBalance","params":[addr,"latest"],"id":1}
		h = self.make_request(skeleton)['result'].encode('ascii','ignore')
		return h if hex_output else int(h, 16)

	# Get full storage state
	# IT LOOKS LIKE THIS ONE NO LONGER EXISTS
	def get_storage(self, addr):
		addr = prepend0x(addr)
		skeleton = {"jsonrpc":"2.0","method":"eth_storageAt","params":[addr],"id":1}
		if self.version > 0.8:
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
		skeleton = {"jsonrpc":"2.0","method":"eth_getStorageAt","params":[addr,index,"latest"],"id":1}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	# Do a simple call (getters)
	def call(self, addr, sig, args, data=None, ethval=0, sender=None):
		return self.transact(addr, ethval, sig, args,
				data=data, sender=sender, is_call=True)

	# Make transaction
	# TODO: this interface sucks
	def transact(self, recip, ethval, sig, args,
			data=None, sender=None, is_call=False,
			secret=None):

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

		# Make transaction call
		skeleton = {"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":ethval,"to":recip,"data":data}],"id":1}
		if sender:
			sender = prepend0x(sender)
			skeleton["params"][0]["from"] = sender
		if secret:
			secret = prepend0x(secret)
			skeleton["params"][0]["secret"] = secret
		if is_call:
			skeleton["method"] = "eth_call"
		return self.make_request(skeleton)['result'].encode('ascii','ignore')
		# return self.make_request(skeleton)


	# Make contract
	def create_contract(self, ethval, code, args=[], sender=None, secret=None):
		
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
		skeleton = {"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":ethval,"data":code}],"id":1}
		if sender:
			sender = prepend0x(sender)
			skeleton["params"][0]["from"] = sender
		if secret:
			secret = prepend0x(secret)
			skeleton["params"][0]["secret"] = secret
		return self.make_request(skeleton)['result'].encode('ascii','ignore')


	# Get the coinbase of the rpc server
	def get_coinbase(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":64}
		return self.make_request(skeleton)['result'].encode('ascii','ignore')

	def get_accounts(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}
		accs = self.make_request(skeleton)['result']
		for i in range(len(accs)):
			accs[i] = accs[i].encode('ascii','ignore')
		return accs

	def is_mining(self):
		skeleton = {"jsonrpc":"2.0","method":"eth_mining","params":[],"id":71}
		return self.make_request(skeleton)['result']



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
			fname = f.get('name') or CONSTRUCTOR_SIG
			self.input_types[fname] = [a['type'] for a in f['inputs']]
			self.input_names[fname] = [a['name'] for a in f['inputs']]
			self.output_types[fname] = [a['type'] for a in f.get('outputs') or []]
			self.output_names[fname] = [a['name'] for a in f.get('outputs') or []]
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
			arg = eu.remove_unicode(args[i])
			if typ in ['uint256','hash256','address','bytes32'] or 'uint' in typ:
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
	def create(cls, code, args, abi, rpc, sender=None, ethval=0, secret=None):
		c = cls(abi, rpc=rpc)
		if args:
			if not CONSTRUCTOR_SIG in c.input_types:
				return None
			code += cls.abi_to_hex(c.input_types, CONSTRUCTOR_SIG, args)[8:]
		c.c_addr = rpc.create_contract(ethval, code, args=[],
				sender=sender, secret=secret)
		return c

	# Make call
	def call(self, fname, args,
			ethval=0, sender=None, c_addr=None):
		return self.transact(
				fname, args, ethval=ethval, sender=sender,
				c_addr=c_addr, is_call=True)

	# Make transaction
	def transact(self, fname, args, ethval=0, sender=None,
			c_addr=None, is_call=False, secret=None):

		# Clean the inputs
		ethval = eu.remove_unicode(ethval)
		sender = eu.remove_unicode(sender)
		secret = eu.remove_unicode(secret)
		c_addr = eu.remove_unicode(c_addr)
		if not c_addr:
			c_addr = self.c_addr

		# Do transaction
		data = Contract.abi_to_hex(self.input_types, fname, args)
		return self.rpc.transact(
				c_addr, ethval, None, None,
				data=data, sender=sender, is_call=is_call, secret=secret)


	# Call, check success, then transact
	def call_then_transact(self, fname, args,
			ethval=0, sender=None, c_addr=None,
			f_success=(lambda x: eu.bool_from_u256(x)),
			f_retval=(lambda x: eu.bool_from_u256(x)),
			secret=None):
		ret = self.call(fname, args, 
				ethval=ethval, sender=sender, c_addr=c_addr)
		if f_success(ret):
			self.transact(fname, args,
					ethval=ethval, sender=sender, c_addr=c_addr,
					secret=secret)
		return f_retval(ret)



#########
## CLI ##
#########

# docopt is awesome
usage_string = \
"""
Ethereum RPC

Usage:
  ethrpc encode_abi <sig> [<params>...] [options]
  ethrpc get_version [options]
  ethrpc get_block_number [options]
  ethrpc get_balance <addr> [options]
  ethrpc get_storage <addr> [options]
  ethrpc get_index <addr> <index> [options]
  ethrpc call <recip> <sig> [<params>...] [options]
  ethrpc transact <recip> <ethval> [<sig> [<params>...]] [options]
  ethrpc create_contract <ethval> <code> [<params>...] [options]
  ethrpc get_accounts [options]
  ethrpc get_coinbase [options]
  ethrpc is_mining [options]

Options:
  -h --help
  -H --host=<host>
  -P --port=<port>
  -s --sender=<sender>
  -S --secret=<secret>
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
	secret = args.get("--secret") or None
	if secret:
		sender = eu.priv_to_addr(secret)
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
			sig, params, data=data, sender=sender, secret=secret)
		sys.stdout.write(str(r))
	elif args['create_contract']:
		r = rpc.create_contract(
			try_int(args["<ethval>"]),
			args["<code>"],
			args=params,
			sender=sender,
			secret=secret)
		sys.stdout.write(str(r))
	elif args['get_accounts']:
		r = rpc.get_accounts()
		sys.stdout.write(str(r))
	elif args['get_coinbase']:
		r = rpc.get_coinbase()
		sys.stdout.write(str(r))
	elif args['get_block_number']:
		r = rpc.get_block_number()
		sys.stdout.write(str(r))
	elif args['get_version']:
		r = rpc.get_version()
		sys.stdout.write(str(r))
	elif args['is_mining']:
		r = rpc.is_mining()
		sys.stdout.write(str(r))

	# Add newline because exta has a terrible prompt
	sys.stdout.write('\n')



# vim: set noexpandtab:
# vim: set tabstop=4:
# vim: set shiftwidth=4:

