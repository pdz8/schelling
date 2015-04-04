from decimal import *
import datetime

from django import forms
from django.conf import settings
from django.contrib import messages, auth
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import timezone

from pyschelling import ethutils as eu
from pyschelling import ethdjango as ed
import ballots.models as bm
import ballots.context_processors as cp
import ballots.notices as notices


######################
## Request handlers ##
######################

def account(request):
	uw = cp.UserWrapper(request)

	# Redirect to force user login
	if not uw.user:
		url = (reverse('social:begin', args=['facebook'])
				+ '?next='
				+ reverse('ballots:account'))
		return redirect(url)

	# Provide empty form or old values
	if request.method == 'GET':
		secret_key = uw.secret_key
		f = AccountForm()
		if secret_key:
			f = AccountForm({'secret_key': secret_key})
		return render(request, 'ballots/account.html', {'f': f})

	# Assume the request is a POST
	# Get new secret key
	f = AccountForm(request.POST)
	if not f.is_valid():
		return render(request, 'ballots/account.html', {'f': f})
	secret_key = f.cleaned_data['secret_key']

	# Update ethereum
	if settings.ENABLE_ETH:
		success = ed.update_voter_for(
				secret_key,
				settings.VOTER_POOL_ADDRESS,
				settings.ADMIN_SECRET,
				timezone.now(),
				old=uw.secret_key)
		if not success:
			messages.error(request, "Ethereum VoterPool update failed")
			return render(request, 'ballots/account.html', {'f': f})

	# Update db
	ea = uw.ethaccount
	if not uw.ethaccount:
		ea = bm.EthAccount(user=uw.user)
	ea.secret_key = secret_key
	ea.address = eu.priv_to_addr(secret_key)
	ea.save()

	messages.success(request, "Your Ethereum secret key is saved.")
	return redirect(reverse('ballots:account'))


def logout(request):
	auth.logout(request)
	return redirect(reverse('ballots:explore'))


def about(request):
	return render(request, 'ballots/about.html')


def ask(request):
	uw = cp.UserWrapper(request)

	# Present empty form
	if request.method == 'GET':
		if not uw.secret_key:
			messages.warning(request, notices.NO_SECRET)
		f = AskForm()
		return render(request, 'ballots/ask.html', {'f':f})

	# Assume POST
	# Get fields and check for errors
	f = AskForm(request.POST)
	if not uw.secret_key:
		messages.error(request, notices.NO_SECRET)
		return render(request, 'ballots/ask.html', {'f':f})
	if not f.is_valid():
		return render(request, 'ballots/ask.html', {'f':f})
	question = f.cleaned_data['question']
	max_option = f.cleaned_data['max_option']
	down_payment = f.cleaned_data['down_payment']
	start_time = f.cleaned_data['start_time']
	commit_period = f.cleaned_data['commit_period']
	reveal_period = f.cleaned_data['reveal_period']

	# Update ethereum
	c_addr = eu.priv_to_addr(eu.keccak(question)) # DEBUG only
	if settings.ENABLE_ETH:
		c_addr = ed.create_ballot(
				eu.secret_key,
				settings.VOTER_POOL_ADDRESS,
				question,
				max_option,
				down_payment,
				start_time,
				commit_period,
				reveal_period)
		if not c_addr:
			messages.error(request, "Failed to create ballot on Ethereum")
			return render(request, 'ballots/ask.html', {'f':f})

	# Update db
	reveal_time = start_time + datetime.timedelta(hours=commit_period)
	redeem_time = reveal_time + datetime.timedelta(hours=reveal_period)
	b = bm.Ballot(
			address=c_addr,
			question=question,
			start_time=start_time,
			reveal_time=reveal_time,
			redeem_time=redeem_time,
			down_payment=down_payment,
			max_option=max_option)
	b.save()

	# Success
	messages.success(request, 'Your ballot has been created.')
	return redirect(reverse('ballots:hex', args=[c_addr]))


def explore(request):
	ballot_list = bm.Ballot.objects.all()
	return render(request, 'ballots/explore.html', {
		'ballot_list': ballot_list,
	})


def vote(request, address=''):
	context = {}
	if not address:
		address = request.GET.get('address') or ''

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
		context['f'] = RevealForm()
		return render(request, 'ballots/vote.html', context)
	
	# Assume we have a POST
	else:
		# TODO: actually handle voting here
		if context['committing']:
			pass
		elif context['revealing']:
			pass
		return redirect('ballots:hex', address=address)


def debug(request):
	messages.error(request, "It looks like we're doomed now. This can't be good.")
	messages.warning(request, "Do ABC to prevent massive failure.")
	messages.success(request, "Everything seems ok. Good job not screwing it up")
	return render(request, 'ballots/about.html')
	# return redirect('ballots:about')


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
			widget=forms.Textarea(attrs={
				'class':'form-control',
				'style':'resize: none'}))
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

