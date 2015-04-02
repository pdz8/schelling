from datetime import datetime, time

import ethnode as en
import ethutils as eu
import ethrpc as er
import contractbin as cb


#########################
## Constants & globals ##
#########################

RPC = er.EthRpc(er.DEFAULT_HOST, er.DEFAULT_PORT)
POOL_CONTRACT = er.Contract(cb.abiVoterPool, rpc=RPC)
BALLOT_CONTRACT = er.Contract(cb.abiDjBallot, rpc=RPC)


#############
## Helpers ##
#############

def datetime_to_utc(dt):
	return int((dt - datetime(1970, 1, 1)).total_seconds())


##################
## Transactions ##
##################

# Add a voter
def add_voter(secret_key, c_addr, entry, old=None):
	sender = eu.priv_to_addr(secret_key)
	with en.ManagerClient(secret_key):
		if not old:
			POOL_CONTRACT.transact(
					'add',
					[entry],
					sender=sender,
					c_addr=c_addr)
		else:
			POOL_CONTRACT.transact(
					'update',
					[entry, old],
					sender=sender,
					c_addr=c_addr)

# Commit to a vote
def submit_hash(secret_key, c_addr, vote_val, nonce):
	sender = eu.priv_to_addr(secret_key)
	nonce_hash = eu.keccak(nonce, False)
	h = BALLOT_CONTRACT.call(
			'get_hash',
			[sender, vote_val, nonce_hash],
			c_addr=c_addr)
	with en.ManagerClient(secret_key):
		BALLOT_CONTRACT.transact(
				'submit_hash',
				[h],
				sender=sender,
				c_addr=c_addr)

# Reveal vote
def reveal_vote(secret_key, c_addr, vote_val, nonce):
	sender = eu.priv_to_addr(secret_key)
	nonce_hash = eu.keccak(nonce, False)
	with en.ManagerClient(secret_key):
		BALLOT_CONTRACT.transact(
				'reveal_hash',
				[vote_val, nonce_hash],
				sender=sender,
				c_addr=c_addr)

# Tally up the votes
def tally(secret_key, c_addr):
	sender = eu.priv_to_addr(secret_key)
	with en.ManagerClient(secret_key):
		BALLOT_CONTRACT.transact(
				'tally_up',
				[],
				sender=sender,
				c_addr=c_addr)


#######################
## Contract creation ##
#######################

# Create a pool
def create_pool(secret_key):
	sender = eu.priv_to_addr(secret_key)
	c = None
	with en.ManagerClient(secret_key):
		c = er.Contract.create(
				cb.binVoterPool,
				[],
				cb.abiVoterPool,
				RPC,
				sender=sender)
	return c.c_addr if c else ''

# Create a ballot
def create_ballot(
		secret_key, pool_addr,
		question, max_option, deposit,
		start_time, commit_period, reveal_period):
	sender = eu.priv_to_addr(secret_key)
	c = None
	args = [
		pool_addr,
		max_option,
		eu.denom_to_wei(deposit, 'ether', True),
		datetime_to_utc(start_time),
		commit_period * 3600,
		reveal_period * 2600,
	] + eu.str_to_string32(question, arr_len=5)


###########
## Calls ##
###########

# Check if voter
def is_voter(c_addr, entry):
	h = POOL_CONTRACT.call('is_voter', [], c_addr=c_addr)
	return eu.bool_from_u256(h)

# Get the tallied decision
def get_decision(c_addr):
	h = BALLOT_CONTRACT.call('get_decision', [], c_addr=c_addr)
	return eu.int_from_u256(h)
