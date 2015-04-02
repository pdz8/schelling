#!/usr/bin/env python
import sys
import re
from subprocess import Popen, PIPE
from docopt import docopt


# Convert solc output to python
# str_in and str_out are input and output streams respectively
cname_pattern = re.compile('======= (?P<cname>.*) =======')
def convert(str_in, str_out, condense=False):
	cname = ''
	binary = False
	abi = False
	for line in str_in:
		m = cname_pattern.match(line)
		if m:
			cname = m.group('cname')
		elif 'Binary:' == line.strip():
			str_out.write('\nbin' + cname + ' = \\\n')
			binary = True
		elif binary:
			str_out.write('"0x' + line.strip() + '"\n')
			binary = False
		elif 'Contract JSON ABI' == line.strip():
			str_out.write('\nabi' + cname + ' = \\\n')
			abi = True
		elif abi:
			line = line.replace('false','False')
			line = line.replace('true','True')
			if condense:
				str_out.write(line.strip())
			else:
				str_out.write(line)
			if ']' == line.rstrip():
				if condense:
					str_out.write('\n')
				abi = False

#########
## CLI ##
#########

usage_string = \
"""
Compile Solidity to Python output

Usage:
  solctopy [(<input> | <input> <output>)] [--min] [--compile]

Options:
  -h --help
  -m --min
  -c --compile
"""

if __name__ == "__main__":
	args = docopt(usage_string)

	# Get args
	in_file = args.get('<input>') or None
	out_file = args.get('<output>') or None
	str_in = open(in_file,'r') if in_file else sys.stdin
	str_out = open(out_file,'w') if out_file else sys.stdout
	comp = args.get('--compile')
	condense = args.get('--min')

	# Compile
	process = None
	if comp:
		if not in_file:
			sys.err.write('Need input file when compiling.')
			sys.exit(1)
		cmd = 'solc --optimize on --input-file {0} --binary stdout --json-abi stdout'.format(in_file)
		process = Popen(cmd.split(), stdout=PIPE)
		str_in = process.stdout

	# Perform conversion
	convert(str_in, str_out, condense=condense)
	str_in.close()
	str_out.close()

