from datetime import datetime, time

import ethnode as en
import ethutils as eu
import ethrpc as er
import contractbin as cb


#############
## Helpers ##
#############

def datetime_to_utc(dt):
	genesis = datetime(1970, 1, 1)
	if dt.tzinfo:
		dt = dt.replace(tzinfo=None) - dt.utcoffset()
	return int((dt - genesis).total_seconds())


#######################
## SchellingCoin API ##
#######################

class SchellingCoin():

	def __init__(self, 
			host=er.DEFAULT_HOST,
			json_port=er.DEFAULT_PORT,
			man_port=en.MANAGER_PORT):
		self.host = host
		self.man_port = man_port
		self.rpc = er.EthRpc(host, json_port)
		self.pool = er.Contract(cb.abiVoterPool, rpc=self.rpc)
		self.ballot = er.Contract(cb.abiDjBallot, rpc=self.rpc)


	##################
	## Transactions ##
	##################

	# Add a voter
	def add_voter(self, secret_key, c_addr, entry, old=None):
		sender = eu.priv_to_addr(secret_key)
		success = False
		if is_voter(c_addr, entry):
			return True
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			if not old:
				success = self.pool.call_then_transact(
						'add',
						[entry],
						sender=sender,
						c_addr=c_addr)
			else:
				success = self.pool.call_then_transact(
						'update',
						[entry, old],
						sender=sender,
						c_addr=c_addr)
		return success


	# Update withe approval of owner
	def update_voter_for(self, secret_key, c_addr, owner_secret, edit_dt, old=None):

		# Format input
		sender = eu.priv_to_addr(secret_key)
		entry = sender
		if not old:
			old = '0'*40
		edit_utc = datetime_to_utc(edit_dt)

		# Create signature
		h = self.pool.call(
				'get_hash',
				[old, entry, edit_utc],
				c_addr=c_addr)
		(v,r,s) = eu.sign(h, owner_secret, do_hash=False)

		# Send transaction
		success = False
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			success = self.pool.call_then_transact(
					'update_for',
					[old, entry, edit_utc, v, r, s],
					sender=sender,
					c_addr=c_addr)
		return success


	# Commit to a vote
	def submit_hash(self, secret_key, c_addr, vote_val, deposit):
		sender = eu.priv_to_addr(secret_key)
		nonce = secret_key + c_addr
		nonce_hash = eu.keccak(nonce, False)
		wei_deposit = eu.denom_to_wei(deposit, 'ether', True)
		h = self.ballot.call(
				'get_hash',
				[sender, vote_val, nonce_hash],
				c_addr=c_addr)
		success = False
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			success = self.ballot.call_then_transact(
					'submit_hash',
					[h],
					sender=sender,
					c_addr=c_addr,
					ethval=wei_deposit)
		return success


	# Reveal vote
	def reveal_vote(self, secret_key, c_addr, vote_val):
		sender = eu.priv_to_addr(secret_key)
		nonce = secret_key + c_addr
		nonce_hash = eu.keccak(nonce, False)
		success = False
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			success = self.ballot.call_then_transact(
					'reveal_hash',
					[vote_val, nonce_hash],
					sender=sender,
					c_addr=c_addr)
		return success


	# Tally up the votes
	def tally(self, secret_key, c_addr):
		sender = eu.priv_to_addr(secret_key)
		decision = 0
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			decision = self.ballot.call_then_transact(
					'tally_up',
					[],
					sender=sender,
					c_addr=c_addr,
					f_retval=(lambda x: eu.int_from_u256(x)))
		return decision


	#######################
	## Contract creation ##
	#######################

	# Create a pool
	def create_pool(self, secret_key):
		sender = eu.priv_to_addr(secret_key)
		c = None
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			c = er.Contract.create(
					cb.binVoterPool,
					[],
					cb.abiVoterPool,
					self.rpc,
					sender=sender)
		return eu.remove0x(c.c_addr) if c else ''

	# Create a ballot
	def create_ballot(self, 
			secret_key, pool_addr,
			question, max_option, deposit,
			start_time, commit_period, reveal_period):
		sender = eu.priv_to_addr(secret_key)
		wei_deposit = eu.denom_to_wei(deposit, 'ether', True)
		c = None
		args = [
			pool_addr,
			max_option,
			wei_deposit,
			datetime_to_utc(start_time),
			commit_period * 60,
			reveal_period * 60,
		] + eu.str_to_string32(question, arr_len=5)
		with en.ManagerClient(secret_key, host=self.host, port=self.man_port):
			c = er.Contract.create(
					cb.binDjBallot,
					args,
					cb.abiDjBallot,
					self.rpc,
					sender=sender,
					ethval=wei_deposit)
		return eu.remove0x(c.c_addr) if c else ''


	################
	## Free calls ##
	################

	# Check if voter
	def is_voter(self, c_addr, entry):
		h = self.pool.call('is_voter', [entry], c_addr=c_addr)
		return eu.bool_from_u256(h)

	# Get the tallied decision
	def get_decision(self, c_addr):
		h = self.ballot.call('get_decision', [], c_addr=c_addr)
		return eu.int_from_u256(h)

	# Get the number of completed votes
	def get_num_revealed(self, c_addr):
		h = self.ballot.call('get_num_revealed', [], c_addr=c_addr)
		return eu.int_from_u256(h)

	# Get account balance
	def get_balance(self, addr):
		try:
			return self.rpc.get_balance(addr)
		except:
			return 0
