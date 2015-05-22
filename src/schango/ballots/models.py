import datetime

from django.db import models
from django.contrib.auth.models import User

import pyschelling.ethdjango as ed
import pyschelling.ethrpc as er
import pyschelling.ethutils as eu
import pyschelling.contractbin as cb


############### TODO: move elsewhere
## Constants ##
###############

MAX_QUESTION_LEN = ed.MAX_QUESTION_LEN


#######################
## Storage models ##
#######################

# Stored representation of ballots
class Ballot(models.Model):
	address = models.CharField(
			max_length=40)
	question = models.CharField(
			max_length=MAX_QUESTION_LEN)
	# start_time = models.DateTimeField()
	# reveal_time = models.DateTimeField()
	# redeem_time = models.DateTimeField()
	start_time = models.PositiveIntegerField()
	reveal_time = models.PositiveIntegerField()
	redeem_time = models.PositiveIntegerField()
	down_payment = models.CharField(
			max_length=64)
	max_option = models.IntegerField()

	decision = models.IntegerField(default=0)
	debug_only = models.BooleanField(default=True)
	is_complete = models.BooleanField(default=False)
	num_revealers = models.IntegerField(default=0)

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

	# Get string representation
	def __str__(self):
		return self.address	

