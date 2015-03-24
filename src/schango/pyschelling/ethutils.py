#!/usr/bin/env python
import sys
import bitcoin as btc
import sha3
import re
from docopt import docopt

# This emulates a lot of the functionality of the fabled pyethereum
# https://github.com/ethereum/pyethereum/blob/master/pyethereum/utils.py


##################
## Crypto utils ##
##################

# sha3
def keccak(x):
	if is_hex(x):
		x = remove0x(x).decode('hex')
	return sha3.sha3_256(x).hexdigest()

# Convert public key to Ethereum address
def pub_to_addr(pub):
	return keccak(pub)[-40:]
	# pub = remove0x(pub).decode('hex')
	# return sha3.sha3_256(pub[1:]).hexdigest()[-40:]

# Convert private key to public key
def priv_to_pub(priv):
	priv = remove0x(priv).decode('hex')
	return btc.privtopub(priv)[1:].encode('hex')

# Convert private key to Ethereum address
def priv_to_addr(priv):
	priv = remove0x(priv).decode('hex')
	pub = btc.privtopub(priv)[1:]
	return sha3.sha3_256(pub).hexdigest()[-40:]

# Sign with secp256k1
# msg should not be packed as hex
def sign(msg, priv):
	if is_hex(msg):
		msg = remove0x(msg).decode('hex')
	priv = remove0x(priv).decode('hex')
	h = sha3.sha3_256(msg).digest()
	v,r,s = btc.ecdsa_raw_sign(h, priv)
	v = removeL(hex(v))
	r = removeL(hex(r))
	s = removeL(hex(s))
	return (v,r,s)

# Recover signing address from msg and sig
def recover(msg, (v,r,s)):
	v = int(v, 16)
	r = int(r, 16)
	s = int(s, 16)
	if is_hex(msg):
		msg = remove0x(msg).decode('hex')
	h = sha3.sha3_256(msg).digest()
	pub = btc.encode_pubkey(btc.ecdsa_raw_recover(h, (v,r,s)), 'hex')
	return pub_to_addr(pub)


####################
## Helper methods ##
####################

# runs regex to detect hex
hex_detect = re.compile('(0x)?([0-9a-fA-F])+')
def is_hex(h):
	return hex_detect.match(h)

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

# Remove the ending L for long
def removeL(s):
	if s.endswith('L'):
		s = s[:-1]
	return s

# Make s have 64 hex characters
def padzeros(s, end=False):
	s = remove0x(s)
	while len(s) < 64:
		if not end:
			s = '0' + s
		else:
			s = s + '0'
	return s

# Convert to int if possible
def try_int(i):
	try:
		int(i)
		return int(i)
	except:
		return i

# Is this a private key
def is_priv(s):
	return is_hex(s) and (len(remove0x(s)) == 64)

# Is this a public key
def is_pub(s):
	return is_hex(s) and (len(remove0x(s)) == 40)
