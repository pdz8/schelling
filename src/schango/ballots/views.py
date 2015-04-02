from decimal import *
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.core.urlresolvers import reverse
import django.contrib.auth as auth

from pyschelling import ethutils as eu
# from ballots.models import Ballot, MAX_QUESTION_LEN, EthAccount, UserWrapper
import ballots.models as bm


#############
## Helpers ##
#############

def get_default_context(request):
	context = {
		'request': request,
		'user': request.user,
		'uw': bm.UserWrapper(request.user),
		'error': '',
	}
	return context


######################
## Request handlers ##
######################

def account(request):
	context = get_default_context(request)
	user = request.user

	# Redirect to force user login
	if not user or not user.id:
		url = (reverse('social:begin', args=['facebook'])
				+ '?next='
				+ reverse('ballots:account'))
		return redirect(url)

	# Provide empty form or old values
	if request.method == 'GET':
		secret_key = ''
		try:
			secret_key = user.ethaccount.secret_key
		except:
			pass
		context['f'] = AccountForm({ 'secret_key': secret_key })
		return render(request, 'ballots/account.html', context)

	# Set new secret key
	else:
		f = AccountForm(request.POST)
		context['f'] = f
		if f.is_valid():
			secret_key = f.cleaned_data['secret_key']
			address = eu.priv_to_addr(secret_key)
			if not hasattr(user, 'ethaccount'):
				ea = bm.EthAccount(
						secret_key=secret_key,
						address=address,
						user=user)
				ea.save()
			else:
				user.ethaccount.secret_key = secret_key
				user.ethaccount.address = address
				user.ethaccount.save()
		return render(request, 'ballots/account.html', context)


def logout(request):
	auth.logout(request)
	return redirect(reverse('ballots:explore'))


def about(request):
	context = get_default_context(request)
	return render(request, 'ballots/about.html', context)


def ask(request):

	# TODO: detect whether user may deposit
	# This involves making a lookup call to the factory
	context = get_default_context(request)

	# Present empty form
	if request.method == 'GET':
		context['f'] = AskForm()
		return render(request, 'ballots/ask.html', context)

	# Assume POST
	else:
		# TODO:
		# 1. Validate user create deposit
		# 2. Create contract - resetting deposit
		# 3. Redirect to vote page
		return redirect('ballots:explore')


def explore(request):
	context = get_default_context(request)
	context['ballot_list'] = ballot_list = bm.Ballot.objects.all()
	return render(request, 'ballots/explore.html', context)


def vote(request, address=""):
	context = get_default_context(request)

	# Retrieve ballot
	address = eu.remove0x(address)
	b = get_object_or_404(bm.Ballot, address=address)
	context['b'] = b
	context['submit_text'] = 'Submit'
	context['f'] = None

	# Detect with phase the ballot is in
	dt = timezone.now()
	context['committing'] = (dt >= b.start_time and dt < b.reveal_time)
	context['revealing'] = (dt >= b.reveal_time and dt < b.redeem_time)
	context['redeeming'] = (dt >= b.reveal_time)

	# TODO: get decision from model or Ethereum
	if context['redeeming']:
		pass

	# Display ballot with empty form
	if request.method == 'GET':
		context['f'] = CommitForm()
		return render(request, 'ballots/vote.html', context)
	
	# Assume we have a POST
	else:
		# TODO: actually handle voting here
		if context['committing']:
			pass
		elif context['revealing']:
			pass
		return redirect('ballots:hex', address=address)


###########
## Forms ##
###########

class AccountForm(forms.Form):
	secret_key = forms.CharField(
			label='Secret Key (hex)',
			max_length=66,
			min_length=64,
			widget=forms.TextInput(attrs={'class':'form-control'}))
			# widget=forms.PasswordInput(attrs={'class':'form-control'}))

class RevealForm(forms.Form):
	vote_val = forms.IntegerField(
			label='Vote Value',
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	nonce = forms.CharField(
			label='Secret Nonce',
			required=True,
			max_length=32,
			widget=forms.TextInput(attrs={'class':'form-control'}))
			# widget=forms.PasswordInput(attrs={'class':'form-control'}))

class CommitForm(RevealForm):
	secret_key = forms.CharField(
			label='Secret Key (hex)',
			max_length=66,
			min_length=64,
			widget=forms.TextInput(attrs={'class':'form-control'}))
			# widget=forms.PasswordInput(attrs={'class':'form-control'}))

class AskForm(forms.Form):
	question = forms.CharField(
			label='Question',
			required=True,
			max_length=bm.MAX_QUESTION_LEN,
			widget=forms.Textarea(attrs={'class':'form-control'}))
	max_option = forms.IntegerField(
			label='Max Option',
			initial=2,
			required=True,
			min_value=2,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	down_payment = forms.DecimalField(
			label='Deposit (ether)',
			initial=Decimal(1.5),
			min_value=Decimal(0),
			required=True,
			decimal_places=18,
			max_digits=100,
			widget=forms.NumberInput(attrs={
					'class':'form-control',
					'step':'0.5'}))
	start_time = forms.DateTimeField(
			label='Start Time',
			initial=timezone.now(),
			required=True,
			widget=forms.DateTimeInput(attrs={'class':'form-control'}))
	commit_period = forms.IntegerField(
			label='Commit Period (hours)',
			initial=24,
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	reveal_period = forms.IntegerField(
			label='Reveal Period (hours)',
			initial=24,
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))

