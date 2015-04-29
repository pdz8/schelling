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
	(question, choices) = bu.parse_question(value, 1)
	return question if question else value

# balance|wei_to_denom:"ether,1"
@register.filter
def wei_to_denom(value, args):
	args = [arg.strip() for arg in args.split(',')]
	denom = args[0]
	max_dec_places = 27
	if len(args) > 1:
		max_dec_places = int(args[1])
	return eu.wei_to_denom(value, denom=denom, max_dec_places=max_dec_places)

@register.filter
@stringfilter
def hwei_to_denom(value, args):
	return wei_to_denom(int(value, 16), args)
