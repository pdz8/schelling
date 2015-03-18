from decimal import *
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.utils import timezone

from pyschelling import ethutils as eu
from ballots.models import Ballot


######################
## Request handlers ##
######################

def create(request):
	pass


def explore(request):
	ballot_list = Ballot.objects.all()
	context = {
		'ballot_list': ballot_list,
	}
	return render(request, 'ballots/explore.html', context)


def vote(request, address=""):

	# Retrieve ballot
	address = eu.prepend0x(address)
	b = get_object_or_404(Ballot, address=address)
	context = {
		'b': b,
		'submit_text': 'Submit',
		'f': None,
	}

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
	
