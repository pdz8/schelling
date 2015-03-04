#!/usr/bin/env python

from setuptools import setup

setup(
	name='SchellingCoin',
	version='0.1',
	package_dir={ 'pyschelling':'src/pyschelling' },
	# py_modules=['ethrpc'],
	install_requires=[
		'docopt',
		'requests',
		'pysha3'],
	url='https://github.com/pdz8/schelling',
	description='Contains components necessary to run SchellingCoin backend.',
	author='Peter Zieske',
	author_email='pdz8@cornell.edu')


# vim: set noexpandtab:
# vim: set tabstop=4:
# vim: set shiftwidth=2:

