from django.conf import settings
from pyschelling import ethdjango as ed


###############
## Constants ##
###############

SCOIN_API = ed.SchellingCoin(host=settings.ETHD_HOST)


####################
## Model wrappers ##
####################

# Simplifies getter access to request.user
class UserWrapper():
	def __init__(self, request, get_bal=False):
		user = request.user

		# Default all fields to None
		self.user = None
		self.ethaccount = None
		self.secret_key = ''
		self.address = ''
		self.fb = None
		self.balance = 0

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
			if get_bal and settings.ENABLE_ETH and self.address:
				self.balance = SCOIN_API.get_balance(self.address)


################
## Processors ##
################

# Apply the user wrapper to the context
def user_processor(request):
	context = {
		'request': request,
		'user': request.user,
		'uw': UserWrapper(request, get_bal=True),
	}
	return context
