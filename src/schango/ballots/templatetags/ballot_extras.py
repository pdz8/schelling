import ballots.utils as bu

from django import template
from django.template.defaultfilters import stringfilter

from pyschelling import ethutils as eu

register = template.Library()


#############
## Filters ##
#############

@register.filter
@stringfilter
def just_question(value):
	(question, choices) = bu.parse_question(value)
	return question if question else value


# hex_balance|wei_to_denom:"ether,1"
@register.filter
@stringfilter
def wei_to_denom(value, args):

	# Convert from hex
	value = int(value, 16)

	# Extract args
	args = [arg.strip() for arg in args.split(',')]
	denom = args[0]
	max_dec_places = 27
	if len(args) > 1:
		max_dec_places = int(args[1])

	# Determine best fit denomination
	if denom == 'best':
		power = 3 * (len(str(value)) / 3)
		denom = eu.POW_DENOM.get(power, eu.POW_DENOM[27])

	# Optionally return just the name of denomination
	if len(args) > 2 and args[2] == 'name':
		return denom

	# Do conversion
	return eu.wei_to_denom(value, denom=denom, max_dec_places=max_dec_places)

