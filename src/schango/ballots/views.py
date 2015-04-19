from decimal import *
import datetime

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
import ballots.forms as bf
import ballots.utils as bu

###############
## Constants ##
###############

SCOIN_API = ed.SchellingCoin(host=settings.ETHD_HOST)

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
		f = bf.AccountForm()
		if secret_key:
			f = bf.AccountForm({'secret_key': secret_key})
		return render(request, 'ballots/account.html', {'f': f})

	# Assume the request is a POST
	# Get new secret key
	f = bf.AccountForm(request.POST)
	if not f.is_valid():
		return render(request, 'ballots/account.html', {'f': f})
	secret_key = f.cleaned_data['secret_key']

	# Update ethereum
	if settings.ENABLE_ETH:
		success = SCOIN_API.update_voter_for(
				secret_key,
				settings.VOTER_POOL_ADDRESS,
				settings.ADMIN_SECRET,
				timezone.now(),
				old=uw.address)
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
		f = bf.AskForm()
		return render(request, 'ballots/ask.html', {'f':f})

	# Assume POST
	# Get fields and check for errors
	f = bf.AskForm(request.POST)
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
		c_addr = SCOIN_API.create_ballot(
				uw.secret_key,
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
	reveal_time = start_time + datetime.timedelta(minutes=commit_period)
	redeem_time = reveal_time + datetime.timedelta(minutes=reveal_period)
	b = bm.Ballot(
			address=c_addr,
			question=question,
			start_time=start_time,
			reveal_time=reveal_time,
			redeem_time=redeem_time,
			down_payment=down_payment,
			max_option=max_option,
			debug_only=not settings.ENABLE_ETH)
	b.save()

	# Success
	messages.success(request, 'Your ballot has been created.')
	return redirect(reverse('ballots:hex', args=[c_addr]))


def explore(request):
	# Pre-fill sort form
	f = None
	if 'filter_by' in request.GET or \
			'q' in request.GET or \
			'sort_by' in request.GET:
		f = bf.SortForm(request.GET)
	else:
		f = bf.SortForm()

	# Do query
	ballot_list = bm.Ballot.objects.all()

	# Render
	return render(request, 'ballots/explore.html', {
		'ballot_list': ballot_list,
		'f': f,
	})


def vote(request, address=''):
	uw = cp.UserWrapper(request)
	context = {}
	if not address:
		address = request.GET.get('address') or ''

	# Retrieve ballot
	address = eu.remove0x(address)
	b = get_object_or_404(bm.Ballot, address=address)
	context['b'] = b
	(question, options) = bu.parse_question(b.question, b.max_option)
	context['question'] = question

	# Detect with phase the ballot is in
	dt = timezone.now()
	context['committing'] = (dt >= b.start_time and dt < b.reveal_time)
	context['revealing'] = (dt >= b.reveal_time and dt < b.redeem_time)
	context['redeeming'] = (dt >= b.reveal_time)
	context['redeemed'] = (b.decision > 0)

	# TODO: get decision from model or Ethereum
	if context['redeeming']:
		pass

	# Display ballot with empty form
	if request.method == 'GET':
		context['f'] = bf.RevealForm(options, )
		return render(request, 'ballots/vote.html', context)
	
	# Assume we have a POST
	# Get fields and check for errors
	context['f'] = f = bf.RevealForm(options, request.POST)
	if not uw.secret_key:
		messages.error(request, notices.NO_SECRET)
		return render(request, 'ballots/vote.html', context)
	if not f.is_valid():
		messages.error(request, notices.FORM_ERROR)
		return render(request, 'ballots/vote.html', context)
	vote_val = f.cleaned_data['vote_val']
	nonce = f.cleaned_data['nonce']

	# TODO: actually handle voting here
	success = True
	if settings.ENABLE_ETH and not b.debug_only:
		if context['committing'] and 'commit' in request.POST:
			success = SCOIN_API.submit_hash(
					uw.secret_key,
					b.address,
					vote_val,
					nonce,
					b.down_payment)
			if not success:
				messages.error(request, notices.COMMIT_ERROR)
			else:
				messages.success(request, notices.COMMIT_SUCCESS)
		elif context['revealing'] and 'reveal' in request.POST:
			success = SCOIN_API.reveal_vote(
					uw.secret_key,
					b.address,
					vote_val,
					nonce)
			if not success:
				messages.error(request, notices.REVEAL_ERROR)
			else:
				messages.success(request, notices.REVEAL_SUCCESS)
		elif context['redeeming'] and 'tally' in request.POST:
			decision = SCOIN_API.get_decision(b.address)
			if decision:
				messages.success(request,'Votes already tallied.')
			elif not SCOIN_API.get_num_revealed(b.address):
				messages.warning(request,'No votes were recorded.')
			else:
				decision = SCOIN_API.tally(uw.secret_key, b.address)
				success = bool(decision)
				if not success:
					messages.error(request, notices.TALLY_ERROR)
				else:
					messages.success(request, notices.TALLY_SUCCESS)
		elif context['redeemed']:
			messages.success(request,'Votes already tallied.')
		else:
			messages.warning(request, notices.TOO_EARLY)
	else:
		messages.success(request, notices.NO_ETH_SUCCESS)

	# Check success
	if not success:
		return render(request, 'ballots/vote.html', context)
	else:
		return redirect('ballots:hex', address=address)


def debug(request):
	messages.error(request, "It looks like we're doomed now. This can't be good.")
	messages.warning(request, "Do ABC to prevent massive failure.")
	messages.success(request, "Everything seems ok. Good job not screwing it up")
	return render(request, 'ballots/about.html')
	# return redirect('ballots:about')

