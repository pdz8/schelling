import ballots.utils as bu

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#############
## Filters ##
#############

@register.filter
@stringfilter
def just_question(value):
	(question, choices) = bu.parse_question(value, 1)
	return question if question else value
