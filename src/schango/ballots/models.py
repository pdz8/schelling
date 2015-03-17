import datetime

from django.db import models

import pyschelling.ethrpc as er
import pyschelling.ethutils as eu
import pyschelling.contractbin as cb


#######################
## Model definitions ##
#######################

# Stored representation of ballots
class Ballot(models.Model):
	address = models.CharField(max_length=42)
	question = models.CharField(max_length=5*32)
	start_time = models.DateTimeField()
	reveal_time = models.DateTimeField()
	redeem_time = models.DateTimeField()
	down_payment = models.DecimalField(max_digits=100,decimal_places=2)
	max_choice = models.IntegerField()

	# Get string representation
	def __str__(self):
		return self.address
	
