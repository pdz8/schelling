import os
import sys
import subprocess
import time
import threading

import ethrpc
import ethutils


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

# Change defaults for Windows
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
			no_output=True,
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
		if append_args:
			self.args += append_args
		self.args += ['-v', '0']

		# Start process
		self.DEVNULL = None
		if no_output:
			self.DEVNULL = open(os.devnull, 'wb')
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
		self.rpc = ethrpc.EthRpc('localhost', json_port)
		self.mutex = threading.Lock()


	# Initialize default node
	@classmethod
	def init_default(cls, load_time=DEFAULT_LOAD_TIME, append_args=[]):
		en = cls(load_time=load_time, append_args=append_args)
		return en


	# Initialize node 2
	@classmethod
	def init_alternate(cls, load_time=DEFAULT_LOAD_TIME, append_args=[]):
		en = cls(
			db_path=ALT_DB_PATH,
			json_port=ALT_JSON_PORT,
			listen_port=ALT_LISTEN_PORT,
			remote_ip=ALT_REMOTE_IP,
			load_time=load_time,
			append_args=append_args)
		return en


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
		priv = ethutils.prepend0x(priv)
		if not ethutils.is_hex(priv):
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

