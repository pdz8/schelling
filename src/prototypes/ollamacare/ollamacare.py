#!/usr/bin/env python
import sys
from docopt import docopt
from pyethereum import ethclient as ec
import serpent

# The JSON-RPC port to connect to
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8080
DEFAULT_GASPRICE = 10 ** 12
DEFAULT_STARTGAS = 10000

# Compiled contract code

# Enables interaction with the farm
class FarmClient:

	def __init__(
			self, pkey,
			host=DEFAULT_HOST, port=DEFAULT_PORT, addr=None):
		self.client = ec.APIClient(host,port)
		self.contract_addr = addr
		self.pkey = pkey

	def create_contract(self, code_file='ollamacare.se'):
		code = serpent.compile(code_file).encode("hex")
		self.contract_addr = self.client.quickcontract(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			0, code, self.pkey)['addr']
		return self.contract_addr

	def set_terms(self,
			payout,
			farm_addr, wthr_auth, temp_tresh, 
			premium, pay_period, num_payments):
		if not self.contract_addr:
			sys.stderr.write("No contract address")
			return
		data = serpent.encode_abi('set_terms','iiiiii',
			farm_addr, wthr_auth, temp_tresh,
			premium, pay_period, num_payments).encode("hex")
		self.client.quicktx(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			self.contract_addr, payout, data, self.pkey)

	def weather_update(self, curr_temp):
		if not self.contract_addr:
			sys.stderr.write("No contract address")
			return
		data = serpent.encode_abi('weather','i',curr_temp).encode("hex")
		self.client.quicktx(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			self.contract_addr, 0, data, self.pkey)

	def pay_premium(self, payment):
		if not self.contract_addr:
			sys.stderr.write("No contract address")
			return
		data = serpent.encode_abi('pay','i',0).encode("hex")
		self.client.quicktx(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			self.contract_addr, payment, data, self.pkey)

	def enforce(self):
		if not self.contract_addr:
			sys.stderr.write("No contract address")
			return
		data = serpent.encode_abi('enforce','i',0).encode("hex")
		self.client.quicktx(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			self.contract_addr, 0, data, self.pkey)

	def kill_contract(self):
		if not self.contract_addr:
			sys.stderr.write("No contract address")
			return
		data = serpent.encode_abi('kill_me','i',0).encode("hex")
		self.client.quicktx(
			DEFAULT_GASPRICE, DEFAULT_STARTGAS,
			self.contract_addr, 0, data, self.pkey)


# docopt is awesome
usage_string = \
"""
OllamaCare

Usage:
  ollamacare create <pkey>
  ollamacare set_terms <pkey> <contract> <payout> <farm_addr> <wthr_auth> 
                       <temp_tresh> <premium> <pay_period> <num_payments>
  ollamacare weather_update <pkey> <contract> <temp>
  ollamacare pay_premium <pkey> <contract> <payment>
  ollamacare enforce <pkey> <contract>
  ollamacare kill <pkey> <contract>

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
	pkey = args.get('<pkey>') or None
	contract = args.get('<contract>') or None
	fc = FarmClient(pkey, host, port, contract)

	# Switch statment
	if args['create']:
		fc.create_contract()
	elif args['set_terms']:
		fc.set_terms(
			args['<payout>'], args['<farm_addr>'], args['<wthr_auth>'], 
			int(args['<temp_tresh>']), int(args['<premium>']),
			int(args['<pay_period>']), int(args['<num_payments>']))
	elif args['weather_update']:
		fc.weather_update(int(args['<temp>']))
	elif args['pay_premium']:
		fc.pay_premium(int(args['<payment>']))
	elif args['enforce']:
		fc.enforce()
	elif args['kill']:
		fc.kill()


