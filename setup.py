#!/usr/bin/env python

from setuptools import setup

setup(
	name='SchellingCoin',
	version='0.1',
	package_dir={ '':'src/pycmd' },
	py_modules=['ethrpc'],
	install_requires=[
		'docopt',
		'requests',
		'pysha3'],
	url='https://github.com/pdz8/schelling',
	description='Contains components necessary to run SchellingCoin backend.',
	author='Peter Zieske',
	author_email='pdz8@cornell.edu')
