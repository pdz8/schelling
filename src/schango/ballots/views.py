from decimal import *
import datetime
import re

from django.conf import settings
from django.contrib import messages, auth
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.template import RequestContext
from django.utils import timezone

from pyschelling import ethutils as eu
from pyschelling import ethdjango as ed
import ballots.models as bm
import ballots.notices as notices
import ballots.forms as bf
import ballots.utils as bu

###############
## Constants ##
###############

SCOIN_API = ed.SchellingCoin(host=settings.ETHD_HOST)


##################
## Account page ##
##################

def account(request):
	context = RequestContext(request)
	uw = context['uw']
	f = bf.AccountForm()
	tf = bf.TransferForm()

	# Redirect to force user login
	if not uw.user:
		url = (reverse('social:begin', args=['facebook'])
				+ '?next='
				+ reverse('ballots:account'))
		return redirect(url)

	# Provide empty form or old values
	if request.method == 'GET':
		secret_key = uw.secret_key
		if secret_key:
			f = bf.AccountForm({'secret_key': secret_key})
		return render_to_response('ballots/account.html',
				{'f': f, 'tf': tf}, context_instance=context)

	##########
	## POST ##
	##########

	# Do ether transfer
	if 'transfer' in request.POST:

		# Extract inputs
		tf = bf.TransferForm(request.POST)
		if not tf.is_valid() or not eu.is_addr(tf.cleaned_data['recipient']):
			messages.error(request, "Transfer form errors")
			return render_to_response('ballots/account.html',
				{'f': f, 'tf': tf}, context_instance=context)
		transfer_amount = eu.denom_to_wei(
				tf.cleaned_data['transfer_amount'],
				tf.cleaned_data['denom'],
				hex_output=True)
		recipient = tf.cleaned_data['recipient']

		# Execute transaction
		if not settings.ENABLE_ETH:
			messages.error(request, "Ethereum not enabled")
			return render_to_response('ballots/account.html',
				{'f': f, 'tf': tf}, context_instance=context)
		success = SCOIN_API.transact(
				secret_key,
				recipient,
				transfer_amount)
		notices.test_success(request, success, action='transfer')
		if not success:
			return render_to_response('ballots/account.html',
					{'f': f, 'tf': tf}, context_instance=context)
		else:
			return redirect(reverse('ballots:account'))


	# Get new secret key
	f = bf.AccountForm(request.POST)
	if not f.is_valid():
		return render_to_response('ballots/account.html',
				{'f': f, 'tf': tf}, context_instance=context)
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
			return render_to_response('ballots/account.html',
					{'f': f, 'tf': tf}, context_instance=context)

	# Update db
	ea = uw.ethaccount
	if not uw.ethaccount:
		ea = bm.EthAccount(user=uw.user)
	ea.secret_key = secret_key
	ea.address = eu.priv_to_addr(secret_key)
	ea.save()

	messages.success(request, "Your Ethereum secret key is saved.")
	return redirect(reverse('ballots:account'))


#######################
## Create new ballot ##
#######################

def ask(request):
	context = RequestContext(request)
	uw = context['uw']

	# Present empty form
	if request.method == 'GET':
		if not uw.can_use_eth():
			messages.warning(request, notices.NOT_REGISTERED)
		f = bf.AskForm()
		return render_to_response('ballots/ask.html',
				{'f':f}, context_instance=context)

	# Assume POST
	# Get fields and check for errors
	f = bf.AskForm(request.POST)
	if settings.ENABLE_ETH and not uw.can_use_eth():
		messages.error(request, notices.NOT_REGISTERED)
		return render_to_response('ballots/ask.html',
				{'f':f}, context_instance=context)
	if not f.is_valid():
		return render_to_response('ballots/ask.html',
				{'f':f}, context_instance=context)
	question = f.cleaned_data['question']
	down_payment = eu.denom_to_wei(
			f.cleaned_data['down_payment'],
			denom=f.cleaned_data['denom'],
			hex_output=True)
	start_time = f.cleaned_data['start_time']
	commit_period = f.cleaned_data['commit_period'] * 60
	reveal_period = f.cleaned_data['reveal_period'] * 60

	# Extract max_option from quest
	(_, options) = bu.parse_question(question)
	if not options:
		messages.error(request, notices.ASK_PARSE_ERROR)
		return render_to_response('ballots/ask.html',
				{'f':f}, context_instance=context)
	max_option = len(options)

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
			return render_to_response('ballots/ask.html',
					{'f':f}, context_instance=context)

	# Update db
	reveal_time = start_time + commit_period
	redeem_time = reveal_time + reveal_period
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


#########################
## Explore all ballots ##
#########################

def explore(request):
	# Pre-fill sort form
	f = None
	if 'filter_by' in request.GET or \
			'q' in request.GET or \
			'sort_by' in request.GET:
		f = bf.SortForm(request.GET)
		if not f.is_valid():
			messages.warning(request, 'Invalid sort and filter parameters')
			return redirect(reverse('ballots:explore'))
	else:
		f = bf.SortForm()

	# Do query
	ballot_list = bm.Ballot.objects.all()

	# Sort and filter
	if hasattr(f, 'cleaned_data'):
		ballot_list = ballot_list.filter(
				question__contains=f.cleaned_data['q'])
		if not 'all' in f.cleaned_data['filter_by']:
			utc_now = ed.datetime_to_utc(timezone.now())
			if not 'unstarted' in f.cleaned_data['filter_by']:
				ballot_list = ballot_list.exclude(start_time__gt=utc_now)
			if not 'committing' in f.cleaned_data['filter_by']:
				ballot_list = ballot_list.exclude(
						start_time__lte=utc_now, reveal_time__gt=utc_now)
			if not 'revealing' in f.cleaned_data['filter_by']:
				ballot_list = ballot_list.exclude(
						reveal_time__lte=utc_now, redeem_time__gt=utc_now)
			if not 'redeeming' in f.cleaned_data['filter_by']:
				ballot_list = ballot_list.exclude(redeem_time__lte=utc_now)
		ballot_list = ballot_list.order_by(f.cleaned_data['sort_by'])

	# Pagination
	paginator = Paginator(ballot_list, 25)
	page_num = request.GET.get('page')
	try:
		ballot_list = paginator.page(page_num)
	except PageNotAnInteger:
		page_num = 1
		ballot_list = paginator.page(page_num)
	except EmptyPage:
		page_num = paginator.num_pages
		ballot_list = paginator(page_num)
	page_nums = bu.surrounding_pages(int(page_num), paginator.num_pages)
	qstring_base = \
			'?' + re.sub(r'&?page=\d+','',request.META['QUERY_STRING']) + '&'

	# Render
	return render(request, 'ballots/explore.html', {
		'ballot_list': ballot_list,
		'f': f,
		'page_nums': page_nums,
		'qstring_base': qstring_base,
	})


#################
## Ballot page ##
#################

def vote(request, address=''):
	context = RequestContext(request)
	uw = context['uw']
	ctx_dict = {}
	if not address:
		address = request.GET.get('address') or ''

	# Retrieve ballot
	address = eu.remove0x(address)
	b = ctx_dict['b'] = get_object_or_404(bm.Ballot, address=address)
	(question, options) = bu.parse_question(
			b.question, max_option=b.max_option)
	ctx_dict['question'] = question
	f = ctx_dict['f'] = bf.RevealForm(options)

	# Detect with phase the ballot is in
	dt = ed.datetime_to_utc(timezone.now())
	ctx_dict['committing'] = (dt >= b.start_time and dt < b.reveal_time)
	ctx_dict['revealing'] = (dt >= b.reveal_time and dt < b.redeem_time)
	ctx_dict['redeeming'] = (dt >= b.reveal_time)
	ctx_dict['redeemed'] = (b.decision > 0)

	# Display ballot with empty form
	if request.method == 'GET':
		return render_to_response('ballots/vote.html',
				ctx_dict, context_instance=context)

	###########################
	## Assume we have a POST ##
	###########################

	# Assert that there is no Ethereum conflict
	if settings.ENABLE_ETH and not uw.can_use_eth():
		messages.error(request, notices.NOT_REGISTERED)
		return render_to_response('ballots/vote.html',
				ctx_dict, context_instance=context)
	use_eth = settings.ENABLE_ETH and uw.can_use_eth() and not b.debug_only
	success = True

	# Handle a tally
	if 'tally' in request.POST:
		if not settings.ENABLE_ETH or b.debug_only:
			messages.error(request, "Cannot tally; Ethereum is disabled.")
			return redirect('ballots:hex', address=address)
		decision = SCOIN_API.get_decision(b.address)
		if decision or ctx_dict['redeemed']:
			messages.success(request,'Votes already tallied.')
		elif not SCOIN_API.get_num_revealed(b.address):
			messages.warning(request,'No votes were recorded.')
		else:
			decision = SCOIN_API.tally(uw.secret_key, b.address)
			success = bool(decision)
			notices.test_success(request, success, action='tally')
		if decision:
			b.decision = decision
			b.save()

	# Handle vote submission
	elif 'commit' in request.POST or 'reveal' in request.POST:

		# Get vote
		ctx_dict['f'] = f = bf.RevealForm(options, request.POST)
		if not f.is_valid():
			messages.error(request, notices.FORM_ERROR)
			return render_to_response('ballots/vote.html',
					ctx_dict, context_instance=context)
		vote_val = f.cleaned_data['vote_val']

		# Commit to vote
		if 'commit' in request.POST and use_eth:
			success = SCOIN_API.submit_hash(
					uw.secret_key,
					b.address,
					vote_val,
					b.down_payment)
			notices.test_success(request, success, action='commit')

		# Reveal vote
		elif use_eth: # and 'reveal' in request.POST
			success = SCOIN_API.reveal_vote(
					uw.secret_key,
					b.address,
					vote_val)
			notices.test_success(request, success, action='reveal')

	# Check success
	if not success:
		return render_to_response('ballots/vote.html',
				ctx_dict, context_instance=context)
	else:
		return redirect('ballots:hex', address=address)


#################
## Minor pages ##
#################

def logout(request):
	auth.logout(request)
	return redirect(reverse('ballots:explore'))

def about(request):
	return render(request, 'ballots/about.html')

def faq(request):
	return render(request, 'ballots/faq.html')

def quickstart(request):
	return render(request, 'ballots/quickstart.html')

def eula(request):
	return render(request, 'ballots/eula.html')

def debug(request):
	messages.error(request, "It looks like we're doomed now. This can't be good.")
	messages.warning(request, "Do ABC to prevent massive failure.")
	messages.success(request, "Everything seems ok. Good job not screwing it up")
	return render(request, 'ballots/about.html')
	# return redirect('ballots:about')

