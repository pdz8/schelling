#!/usr/bin/env python
import os
import sys
import subprocess
import time
from threading import Lock, Condition, Thread
import socket
from docopt import docopt

import ethrpc as er
import ethutils as eu


#############
## Globals ##
#############

# UNIX eth defaults
DEFAULT_ETH_EXE = '/usr/bin/eth'
DEFAULT_DB_PATH = '~/.ethereum'
DEFAULT_JSON_PORT = 8080
DEFAULT_LISTEN_PORT = 30303
DEFAULT_REMOTE_IP = '5.1.83.225'
DEFAULT_REMOTE_PORT = 30303
DEFAULT_LOAD_TIME = 4 # wait for eth to startup
DEFAULT_COINBASE = '1d6f390b1d4acfc2b8de0de51ecec83fa066f790'

# Change defaults for Windows
if sys.platform in ['win32','cygwin']:
	DEFAULT_ETH_EXE = 'eth'
	DEFAULT_DB_PATH = os.getenv('APPDATA') + '\\Ethereum'
	if sys.platform == 'win32':
		pass
	elif sys.platform == 'cygwin':
		pass

# Default alternates
ALT_DB_PATH = DEFAULT_DB_PATH + '2'
ALT_JSON_PORT = DEFAULT_JSON_PORT + 1
ALT_LISTEN_PORT = DEFAULT_LISTEN_PORT + 1
ALT_REMOTE_IP = '127.0.0.1'


#####################
## Instance of eth ##
#####################

class EthNode():

	# Start a node
	def __init__(
			self,
			eth_exe=DEFAULT_ETH_EXE,
			db_path=None,
			json_port=DEFAULT_JSON_PORT,
			listen_port=DEFAULT_LISTEN_PORT,
			remote_ip=None,
			remote_port=DEFAULT_REMOTE_PORT,
			secret=None,
			interact=True,
			mine=False,
			coinbase=DEFAULT_COINBASE,
			verbosity=0, 
			append_args=[],
			load_time=DEFAULT_LOAD_TIME):
		# Save inputs
		self.eth_exe = eth_exe
		# self.db_path = db_path
		self.json_port = json_port
		self.listen_port = listen_port
		# self.remote_ip = remote_ip
		# self.remote_port = remote_port

		# Create arg list
		self.args = [eth_exe]
		if db_path:
			self.args += ['-d', db_path]
		if json_port:
			self.args += ['-j','--json-rpc-port', str(json_port)]
		if listen_port:
			self.args += ['-l', str(listen_port)]
		if remote_ip and remote_port:
			self.args += ['-r', remote_ip, '-p', str(remote_port)]
		if secret:
			self.args += ['-s', secret]
		if interact:
			self.args += ['-i']
		if mine:
			self.args += ['-m', 'on']
		if coinbase:
			self.args += ['-a', coinbase]
		if append_args:
			self.args += append_args
		if verbosity < 4:
			self.args += ['-v', '0']

		# Start process
		self.DEVNULL = open(os.devnull, 'wb')
		if verbosity < 3:
			self.process = subprocess.Popen(
				self.args,
				stdin=subprocess.PIPE,
				# stdout=subprocess.PIPE,
				stdout=self.DEVNULL,
				stderr=self.DEVNULL)
		else:
			self.process = subprocess.Popen(
					self.args,
					stdin=subprocess.PIPE)

		# Wait for initializations
		time.sleep(load_time)

		# Additional fields
		self.rpc = er.EthRpc('localhost', json_port)
		self.mutex = Lock()


	# Initialize default node
	@classmethod
	def init_default(cls, 
			load_time=DEFAULT_LOAD_TIME,
			append_args=[],
			coinbase=DEFAULT_COINBASE,
			verbosity=0):
		node = cls(load_time=load_time, append_args=append_args, verbosity=verbosity)
		node.input_cmd('minestart')
		return node


	# Initialize node 2
	@classmethod
	def init_alternate(cls, 
			load_time=DEFAULT_LOAD_TIME,
			append_args=[],
			coinbase=DEFAULT_COINBASE,
			verbosity=0):
		node = cls(
			db_path=ALT_DB_PATH,
			json_port=ALT_JSON_PORT,
			listen_port=ALT_LISTEN_PORT,
			remote_ip=ALT_REMOTE_IP,
			load_time=load_time,
			append_args=append_args,
			verbosity=verbosity)
		node.input_cmd('minestart')
		return node


	# Send command to the eth console
	# True iff successful
	def input_cmd(self, cmd, raw=False):
		retval = True
		with self.mutex:
			try:
				# Get the prompt
				if not raw:
					self.process.stdin.write('\n')
					self.process.stdin.flush()
					# c = None
					# while c != '>':
					# 	c = self.process.stdout.read(1)
					# 	if not c:
					# 		raise Exception('EOF')
					time.sleep(0.25) # Let the prompt appear

				# Submit command
				self.process.stdin.write(cmd)
				if not raw:
					self.process.stdin.write('\n')
				self.process.stdin.flush()

			except:
				retval = False
		return retval


	# Set secret key
	def set_secret(self, priv, reset_json=True):
		# Format command
		priv = eu.prepend0x(priv)
		if not eu.is_hex(priv):
			return False
		cmd = 'setSecret ' + priv

		# Execute
		retval = self.input_cmd(cmd)
		if not reset_json or not retval:
			return retval

		# Reset JSON RPC to make changes show up
		if not self.input_cmd('jsonstop'):
			return False
		return self.input_cmd('jsonstart ' + str(self.json_port))



	# Is this alive
	def is_alive(self):
		retval = True
		with self.mutex:
			try:
				retval = (self.process.poll() == None)
			except:
				retval = False
		return retval


	# Kill it now
	def kill(self, graceful=False):
		if not graceful:
			with self.mutex:
				try:
					self.process.terminate()
				except:
					pass
		else:
			self.input_cmd('exit')
		try:
			self.DEVNULL.close()
		except:
			pass


##################
## Node manager ##
##################

# This daemon process manages a ethnode
# It allows setting the secret for the duration of a connection

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 8089
LOCK_MSG = 'LOCK'
UNLOCK_MSG = 'UNLOCK'

# Verbose printing
class VerbosePrinter():
	def __init__(self, level):
		self.level = level

	def out(self, msg, threshold=1):
		if threshold <= self.level:
			sys.stdout.write(msg)

	def err(self, msg, threshold=1):
		if threshold <= self.level:
			sys.stderr.write(msg)


# Runs the simple protocol
class ConnectionHandler(Thread):
	def __init__(self, manager):
		Thread.__init__(self)
		self.setDaemon(True)
		self.manager = manager

	def run(self):
		clientsocket = None
		while True:
			try:
				# Get the client connection
				with self.manager.mutex:
					while not self.manager.work_queue:
						self.manager.work_ready.wait()
					clientsocket = self.manager.work_queue.pop(0)

				# Receive the secret key
				secret_key = ''
				while len(secret_key) < 64:
					secret_key += clientsocket.recv(64 - len(secret_key))
				addr = eu.priv_to_addr(secret_key)
				self.manager.vp.out('LOCK on ' + addr + '\n', 2)

				# Set the secret key
				self.manager.node.set_secret(secret_key)

				# Acknowledge secret key
				clientsocket.send(LOCK_MSG.encode('utf-8'))

				# Receive unlock from client
				data = ''
				while len(data) < len(UNLOCK_MSG):
					data += clientsocket.recv(len(UNLOCK_MSG) - len(data))
				clientsocket.close()
				self.manager.vp.out('UNLOCK\n', 2)

				# Reset the key to avoid exploits
				if (self.manager.reset_key):
					self.manager.node.set_secret(self.manager.reset_key)
			except:
				self.manager.vp.err('Error in ethnode conn-handler\n', 0)
				break


# Server manager
class ManagerServer:
	def __init__(self, node, vp=VerbosePrinter(1), reset_key=False,
				host=MANAGER_HOST, port=MANAGER_PORT,
				allowed_ip=MANAGER_HOST):
		self.node = node
		self.work_queue = []
		self.mutex = Lock()
		self.work_ready = Condition(self.mutex)
		self.vp = vp
		self.reset_key = eu.keccak('reset_key') if reset_key else None
		self.host = host
		self.port = port
		self.allowed_ip = socket.gethostbyname(allowed_ip)

	def run_loop(self):
		# Startup socket
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind((self.host, self.port))
		serversocket.listen(5)

		# Start worker
		conn_handler = ConnectionHandler(self)
		conn_handler.start()

		# Actual loop
		while True:
			try:
				(clientsocket, address) = serversocket.accept()
				if address[0] != self.allowed_ip and address[0] != '127.0.0.1':
				# if address[0] != self.allowed_ip:
					self.vp.err('Disallowed IP {0} attempted to connect\n'
							.format(address[0]))
					clientsocket.close()
					continue
			except:
				break
			with self.mutex:
				self.work_queue.append(clientsocket)
				self.work_ready.notify()


# Client for server manager
class ManagerClient:
	def __init__(self, secret_key, host=MANAGER_HOST, port=MANAGER_PORT):
		self.secret_key = secret_key
		self.host = host
		self.port = port
		self.sock = None

	def lock(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		self.sock.send(self.secret_key.encode('utf-8'))
		data = ''
		while len(data) < len(LOCK_MSG):
			data += self.sock.recv(len(LOCK_MSG) - len(data))

	def unlock(self):
		self.sock.send(UNLOCK_MSG.encode('utf-8'))
		self.sock.close()

	def __enter__(self):
		self.lock()

	def __exit__(self, type, value, traceback):
		self.unlock()
		return True

#########
## CLI ##
#########

usage_string = \
"""
Ethereum node manager for CrowdVerity

Usage:
  ethnode [options]

Options:
  -h --help               Show this message
  -v --verbosity=<level>  Set the verbosity [default: 1]
  -c --coinbase=<addr>    Set the coinbase for mining
  -R --reset_key          Reset the secret key after unlock
  -H --host=<host>        Host to bind on [default: 0.0.0.0]
  -P --port=<port>        Port to bind on [default: 8089]
  -A --allowed_ip=<host>  Host to accept [default: 127.0.0.1]
"""

if __name__ == "__main__":
	args = docopt(usage_string)

	# Setup printer
	verbosity = 1
	if args['--verbosity'] is not None:
		verbosity = int(args['--verbosity'])
	vp = VerbosePrinter(verbosity)

	# Setup coinbase
	coinbase = DEFAULT_COINBASE
	if args['--coinbase'] and eu.is_addr(args['--coinbase']):
		coinbase = args['--coinbase']

	# Start server
	vp.out('Starting Ethereum node...\n')
	node = EthNode.init_default(
			verbosity=verbosity,
			coinbase=coinbase)
	if node.is_alive():
		vp.out('Ethereum node running\n')
	else:
		vp.err('Failure: Could not start node\n', 0)
		sys.exit(1)
	manager = ManagerServer(
			node,
			vp=vp,
			reset_key=args['--reset_key'],
			host=args['--host'],
			port=int(args['--port']),
			allowed_ip=args['--allowed_ip'])
	vp.out('Manager server loop started\n')
	manager.run_loop()
