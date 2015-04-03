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
	success = False
	if is_voter(c_addr, entry):
		return True
	with en.ManagerClient(secret_key):
		if not old:
			ret = POOL_CONTRACT.transact(
					'add',
					[entry],
					sender=sender,
					c_addr=c_addr)
		else:
			ret = POOL_CONTRACT.transact(
					'update',
					[entry, old],
					sender=sender,
					c_addr=c_addr)
		success = eu.bool_from_u256(ret)
	return success


# Update withe approval of owner
def update_voter_for(secret_key, c_addr, owner_secret, edit_dt, old=None):

	# Format input
	sender = eu.priv_to_addr(secret_key)
	entry = sender
	if not old:
		old = '0'*40
	edit_utc = hex(datetime_to_utc(edit_dt))

	# Create signature
	msg = (eu.hex_to_bytes(c_addr)
			+ eu.hex_to_bytes(old)
			+ eu.hex_to_bytes(entry)
			+ eu.hex_to_bytes(edit_utc))
	(v,r,s) = eu.sign(msg, owner_secret)

	# Send transaction
	success = False
	with en.ManagerClient(secret_key):
		ret = POOL_CONTRACT.transact(
				'update_for',
				[old, entry, edit_utc, v, r, s],
				sender=sender,
				c_addr=c_addr)
		success = eu.bool_from_u256(ret)
	return success


# Commit to a vote
def submit_hash(secret_key, c_addr, vote_val, nonce, deposit):
	sender = eu.priv_to_addr(secret_key)
	nonce_hash = eu.keccak(nonce, False)
	wei_deposit = eu.denom_to_wei(deposit, 'ether', True)
	h = BALLOT_CONTRACT.call(
			'get_hash',
			[sender, vote_val, nonce_hash],
			c_addr=c_addr)
	success = False
	with en.ManagerClient(secret_key):
		ret = BALLOT_CONTRACT.transact(
				'submit_hash',
				[h],
				sender=sender,
				c_addr=c_addr,
				ethval=wei_deposit)
		success = eu.bool_from_u256(ret)
	return success


# Reveal vote
def reveal_vote(secret_key, c_addr, vote_val, nonce):
	sender = eu.priv_to_addr(secret_key)
	nonce_hash = eu.keccak(nonce, False)
	success = False
	with en.ManagerClient(secret_key):
		ret = BALLOT_CONTRACT.transact(
				'reveal_hash',
				[vote_val, nonce_hash],
				sender=sender,
				c_addr=c_addr)
		success = eu.bool_from_u256(ret)
	return success


# Tally up the votes
def tally(secret_key, c_addr):
	sender = eu.priv_to_addr(secret_key)
	decision = 0
	with en.ManagerClient(secret_key):
		ret = BALLOT_CONTRACT.transact(
				'tally_up',
				[],
				sender=sender,
				c_addr=c_addr)
		decision = eu.int_from_u256(ret)
	return decision


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
	wei_deposit = eu.denom_to_wei(deposit, 'ether', True)
	c = None
	args = [
		pool_addr,
		max_option,
		wei_deposit,
		datetime_to_utc(start_time),
		commit_period * 3600,
		reveal_period * 3600,
	] + eu.str_to_string32(question, arr_len=5)
	with en.ManagerClient(secret_key):
		c = er.Contract.create(
				cb.binDjBallot,
				[],
				cb.abiDjBallot,
				RPC,
				sender=sender,
				ethval=wei_deposit)
	return c.c_addr if c else ''


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
