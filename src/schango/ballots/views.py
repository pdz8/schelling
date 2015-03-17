from decimal import *
import datetime

from django.shortcuts import render, get_object_or_404
from django import forms
from django.utils import timezone

from ballots.models import Ballot


######################
## Request handlers ##
######################

def create(request):
	pass


def explore(request):
	b_list = [
		Ballot(
			address="0x99a67a0d37b4b2a79ce1b2c17f472ba1813093d3",
			question="Will Kentucky with it all? 1-yes 2-no",
			start_time=timezone.now(),
			reveal_time=timezone.now() + datetime.timedelta(days=1),
			redeem_time=timezone.now() + datetime.timedelta(days=2),
			down_payment=Decimal(5000),
			max_choice=2),
		Ballot(
			address="0xe6389d124a71c6f5f671cbc0a5a6fb22aac80ff4",
			question="Will the Lions win the SuperBowl? 1-yes 2-no",
			start_time=timezone.now(),
			reveal_time=timezone.now() + datetime.timedelta(days=1),
			redeem_time=timezone.now() + datetime.timedelta(days=2),
			down_payment=Decimal(5000),
			max_choice=2),
	]
	context = {
		'ballot_list': b_list,
	}
	return render(request, 'ballots/explore.html', context)


def vote(request):
	pass
