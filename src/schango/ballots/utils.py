# import re


# Parse question text into a list of names a values
# e.g. The sky is blue. 1-True 2-False
def parse_question(s, max_option=None):
	# Parse the max option if necessary
	if not max_option:
		max_option = 0
		while s.find(str(max_option + 1) + '-'):
			max_option += 1

	# Validate input
	if not max_option >= 1:
		return (None, None)

	# Extract options
	try:
		[question_text, s] = s.split('1-', 2)
		options = []
		for i in range(1, max_option):
			[option_text, s] = s.split(str(i + 1) + '-', 2)
			options.append((i, option_text.strip()))
		options.append((max_option, s.strip()))
		return (question_text.strip(), options)
	except:
		return (None, None)

