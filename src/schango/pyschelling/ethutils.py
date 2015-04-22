#!/usr/bin/env python
import sys
import re
import decimal
import os

import sha3
import pybitcointools as btc
from docopt import docopt

# This emulates a lot of the functionality of the fabled pyethereum
# https://github.com/ethereum/pyethereum/blob/master/pyethereum/utils.py


##################
## Crypto utils ##
##################

# Create new Ethereum account
def gen_secret():
	return os.urandom(32).encode('hex')

# sha3
def keccak(x, treat_as_hex=True):
	if isinstance(x, unicode):
		x = x.encode('utf-8', 'ignore')
	if is_hex(x) and treat_as_hex:
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
def sign(h, priv, do_hash=False):
	if is_hex(h):
		h = remove0x(h).decode('hex')
	if do_hash:
		h = sha3.sha3_256(h).digest()
	priv = remove0x(priv).decode('hex')
	v,r,s = btc.ecdsa_raw_sign(h, priv)
	v = removeL(hex(v))
	r = removeL(hex(r))
	s = removeL(hex(s))
	return (v,r,s)

# Recover signing address from msg and sig
def recover(h, tup, do_hash=False):
	(v,r,s) = tup
	v = int(v, 16)
	r = int(r, 16)
	s = int(s, 16)
	if is_hex(h):
		h = remove0x(h).decode('hex')
	if do_hash:
		h = sha3.sha3_256(h).digest()
	pub = btc.encode_pubkey(btc.ecdsa_raw_recover(h, (v,r,s)), 'hex')
	return pub_to_addr(pub[2:])


#################################
## Conversion to and from u256 ##
#################################

# Split u256 hex into list of 32 bytes each
def split_u256(h, arr_len=None):
	h = remove0x(h)
	retval = []
	while h:
		if len(h) >= 64:
			retval += [h[:64]]
			h = h[64:]
		else:
			retval += [h + ('0'*(64 - len(h)))]
			h = None
	if arr_len and arr_len > len(retval):
		retval += ['0'*64]*(arr_len - len(retval))
	if arr_len and arr_len < len(retval):
		retval = retval[:arr_len]
	return retval

# Split a string into u256 arrays
def str_to_u256(s, arr_len=None):
	h = s.encode('hex')
	return split_u256(h, arr_len=arr_len)

# Split a string into string32's
def str_to_string32(s, arr_len=None):
	return [h.decode('hex') for h in str_to_u256(s, arr_len=arr_len)]

# Take appended u256 integers and pull out the encoded string
def str_from_u256(h):
	s = (remove0x(h)).decode('hex')
	s = s.replace('\x00','')
	return s

# Extract integer
def int_from_u256(h):
	h = remove0x(h)
	if h == '':
		return 0 # TODO this is a hack
	return int(h,16)

# Extract boolean
def bool_from_u256(h):
	return bool(int_from_u256(h))


####################
## Helper methods ##
####################

# runs regex to detect hex
hex_detect = re.compile('^(0x)?([0-9a-fA-F])+$')
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

# Is this an address
def is_addr(s):
	return is_hex(s) and (len(remove0x(s)) == 40)

# Convert hex string to byte string
def hex_to_bytes(h):
	return removeL(remove0x(h)).decode('hex')

# Remove unicode
def remove_unicode(s):
	if isinstance(s, unicode):
		# if is_hex(s):
		# 	return s.decode('hex').encode('hex')
		s = s.encode('utf-8', 'ignore')
	return s


#########################
## Currency conversion ##
#########################

DENOM_POW = {
	'wei': 0,
	'kwei': 3,
	'mwei': 6,
	'gwei': 9,
	'szabo': 12,
	'finney': 15,
	'ether': 18,
	'grand': 21,
	'mether': 24,
	'gether': 27,
}

# Convert ethereum denomination to Wei
# Avoids floating point errors
# This works with decimal type!
def denom_to_wei(val, denom='ether', hex_output=False):
	sval = str(val)
	if sval.find('.') < 0:
		sval = sval + '.'
	[whole,dec] = sval.split('.')
	dpow = DENOM_POW[denom.lower()]
	if dpow <= len(dec):
		dec = dec[:dpow]
	else:
		dec += ('0' * (dpow - len(dec)))
	i = int(whole + dec)
	if hex_output:
		return removeL(hex(i))
	else:
		return i

# Convtert wei to etherum denomination
# This returns a string to avoid floating point mess
# This works with decimal type!
def wei_to_denom(val,
		denom='ether',
		max_dec_places=27,
		out_decimal=False):
	# Convert
	sval = removeL(str(val))
	denom = denom.lower()
	dec = DENOM_POW[denom] if denom in DENOM_POW else DENOM_POW['ether']
	if len(sval) < dec + 1:
		sval = ('0' * (dec + 1 - len(sval))) + sval
	sval = sval[:-dec] + '.' + sval[-dec:]

	# Output
	if dec > max_dec_places:
		sval = sval[:-(dec - max_dec_places)]
	if out_decimal:
		return decimal.Decimal(sval)
	else:
		return sval


