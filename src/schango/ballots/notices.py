from django.contrib import messages


##############
## Warnings ##
##############

TOO_EARLY = "Action is not enabled at this time."


############
## Errors ##
############

NOT_REGISTERED = \
	"You need to complete your account setup to interact with Ethereum. " \
	"This includes registering an address and having an available balance."
COMMIT_ERROR = "Could not complete commit on Ethereum."
REVEAL_ERROR = "Could not complete reveal on Ethereum."
TALLY_ERROR = "Could not complete tally on Ethereum."
FORM_ERROR = "There were form errors in your request."
ASK_PARSE_ERROR = "Could not parse options from submitted question."
ETH_REQ_ERROR = "Could not complete request on Ethereum."

#####################
## Success stories ##
#####################

COMMIT_SUCCESS = "Commit was processed on Ethereum."
REVEAL_SUCCESS = "Reveal was processed on Ethereum."
TALLY_SUCCESS = "Votes tallied on Ethereum. Thank you!"
NO_ETH_SUCCESS = "Action completed but Ethereum is disabled."
ETH_REQ_SUCCESS = "Request accepted by Ethereum."


##################
## Example text ##
##################

ASK_TEMPLATE = \
"""Use #-Option format to specify options. An example is:

Is the sky blue?
1-Yeah duh
2-No, not at midnight"""


####################
## Helper methods ##
####################

ERROR_DICT = {
	'reveal': REVEAL_ERROR,
	'commit': COMMIT_ERROR,
	'tally': TALLY_ERROR,
}
SUCCESS_DICT = {
	'reveal': REVEAL_SUCCESS,
	'commit': COMMIT_SUCCESS,
	'tally': TALLY_SUCCESS,
}

# Easier way to post light error/success messages
def test_success(request, success, action=None,
		error_msg=None, success_msg=None):
	# Get messages
	if action:
		error_msg = ERROR_DICT[action]
		success_msg = SUCCESS_DICT[action]

	# Append messages
	if success:
		messages.success(request, success_msg)
	else:
		messages.error(request, error_msg)

