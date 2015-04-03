####################
## Model wrappers ##
####################

# Simplifies getter access to request.user
class UserWrapper():
	def __init__(self, request):
		user = request.user

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


################
## Processors ##
################

# Apply the user wrapper to the context
def user_processor(request):
	context = {
		'request': request,
		'user': request.user,
		'uw': UserWrapper(request),
	}
	return context
