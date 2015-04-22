from django.conf import settings

from pyschelling import ethdjango as ed
from pyschelling import ethutils as eu
import ballots.models as bm


###############
## Constants ##
###############

SCOIN_API = ed.SchellingCoin(host=settings.ETHD_HOST)


####################
## Model wrappers ##
####################

# Simplifies getter access to request.user
class UserWrapper():
	def __init__(self, request, call_eth=False):
		user = request.user

		# Default all fields to None
		self.user = None
		self.ethaccount = None
		self.secret_key = ''
		self.address = ''
		self.fb = None
		self.balance = 0
		self.is_registered = False

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
			if call_eth and settings.ENABLE_ETH and self.address:
				self.balance = SCOIN_API.get_balance(self.address)
				if settings.VOTER_POOL_ADDRESS:
					self.is_registered = ed.is_voter(
							settings.VOTER_POOL_ADDRESS,
							self.address)

	def gen_eth_account(self):
		if self.user and not self.ethaccount:
			self.ethaccount = bm.EthAccount(user=self.user)
			self.ethaccount.secret_key = self.secret_key = eu.gen_secret()
			self.ethaccount.address = self.address = eu.priv_to_addr(
					self.secret_key)
			self.ethaccount.save()

	def can_use_eth(self):
		return self.balance and self.is_registered


################
## Processors ##
################

# Apply the user wrapper to the context
def user_processor(request):
	uw = UserWrapper(request, call_eth=True)

	# Generate default Ethereum account
	uw.gen_eth_account()

	# Update context
	context = {
		'request': request,
		'user': request.user,
		'uw': uw,
	}
	return context
