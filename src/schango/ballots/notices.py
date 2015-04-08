from django.contrib import messages


####################
## Helper methods ##
####################

def test_success(request, success, good, bad):
	if success:
		messages.success(request, good)
	else:
		messages.error(request, bad)


##############
## Warnings ##
##############

TOO_EARLY = "Hold you horses. Voting hasn't begun yet."


############
## Errors ##
############

NO_SECRET = \
"You do not have an Ethereum secret associated with your account. \
An Ethereum secret is needed to interact with Ethereum."
COMMIT_ERROR = "Could not complete commit on Ethereum."
REVEAL_ERROR = "Could not complete reveal on Ethereum."
TALLY_ERROR = "Could not complete tally on Ethereum."
FORM_ERROR = "There were form errors in your request."


#####################
## Success stories ##
#####################

COMMIT_SUCCESS = "Commit was processed on Ethereum."
REVEAL_SUCCESS = "Reveal was processed on Ethereum."
TALLY_SUCCESS = "Votes tallied on Ethereum. Thank you!"
NO_ETH_SUCCESS = "Action completed but Ethereum is disabled."
