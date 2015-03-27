#!/usr/bin/env python
import sys
import re
from subprocess import Popen, PIPE


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


if __name__ == "__main__":
	# Get args
	str_in = sys.stdin
	str_out = sys.stdout
	condense = False
	comp = False
	in_file = None
	for arg in sys.argv[1:]:
		if arg in ['-m','--min']:
			condense = True
		elif arg in ['-c','--compile']:
			comp = True
		elif str_in is sys.stdin:
			in_file = arg
			str_in = open(arg,'r')
		elif str_out is sys.stdout:
			str_out = open(arg,'w')

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

