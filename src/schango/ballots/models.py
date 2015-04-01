import datetime

from django.db import models
from django.contrib.auth.models import User

import pyschelling.ethrpc as er
import pyschelling.ethutils as eu
import pyschelling.contractbin as cb


############### TODO: move elsewhere
## Constants ##
###############

MAX_QUESTION_LEN = 5*32


#######################
## Storage models ##
#######################

# Stored representation of ballots
class Ballot(models.Model):
	address = models.CharField(
			max_length=40)
	question = models.CharField(
			max_length=MAX_QUESTION_LEN)
	start_time = models.DateTimeField()
	reveal_time = models.DateTimeField()
	redeem_time = models.DateTimeField()
	down_payment = models.DecimalField(
			'Ether deposit',
			max_digits=100,
			decimal_places=18)
	max_choice = models.IntegerField()

	# Get string representation
	def __str__(self):
		return self.address

# Represents an Ethereum account
class EthAccount(models.Model):
	address = models.CharField(
			max_length=42)
	secret_key = models.CharField(
			max_length=66)
	user = models.OneToOneField(User)


####################
## Model wrappers ##
####################

# Simplifies getter access to request.user
class UserWrapper():
	def __init__(self, user):
		# Default all fields to None
		self.user = None
		self.ethaccount = None
		self.secret_key = ''
		self.address = ''
		self.fb = None

		# Get user if available
		if user and user.id:
			self.user = user

		# Get Facebook attributes
		if hasattr(user, 'social_auth'):
			try:
				self.fb = user.social_auth.get(provider='facebook')
			except:
				pass

		# Get Ethereum attributes
		if hasattr(user, 'ethaccount'):
			self.ethaccount = user.ethaccount
			self.secret_key = user.ethaccount.secret_key
			self.address = user.ethaccount.address

