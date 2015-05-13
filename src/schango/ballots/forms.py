from decimal import *

from django import forms
from django.utils import timezone

import ballots.models as bm
import ballots.notices as notices

###############
## Constants ##
###############

DENOM_OPTIONS = [
	('wei', 'wei'),
	('kwei', 'Kwei'),
	('mwei', 'Mwei'),
	('gwei', 'Gwei'),
	('szabo', 'szabo'),
	('finney', 'finney'),
	('ether', 'ether'),
	('grand', 'grand'),
	('mether', 'Mether'),
	('gether', 'Gether'),
]

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

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(AccountForm, self).__init__(*args, **kwargs)


class RevealForm(forms.Form):
	vote_val = forms.IntegerField(
			label='Vote Value',
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	
	def __init__(self, choices, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(RevealForm, self).__init__(*args, **kwargs)
		if choices:
			self.fields['vote_val'] = forms.TypedChoiceField(
					label='Vote Value',
					required=True,
					coerce=int,
					choices=choices,
					empty_value=0,
					widget=forms.RadioSelect(
						# attrs={'class':'form-control'}
					))

class SortForm(forms.Form):
	q = forms.CharField(
			label='Question Contains',
			required=False,
			max_length=bm.MAX_QUESTION_LEN,
			widget=forms.TextInput(attrs={'class':'form-control'}))
	sort_by = forms.ChoiceField(
			label='Sort By',
			required=False,
			choices=[
				('start_time', 'Start Time'),
				('reveal_time', 'Reveal Time'),
				('redeem_time', 'Reedeem Time'),
			],
			initial='start_time',
			widget=forms.Select(attrs={'class':'form-control'}))
	filter_by = forms.MultipleChoiceField(
			label='Filter',
			required=False,
			choices=[
				('all','All'),
				('unstarted', 'Unstarted'),
				('committing','Committing'),
				('revealing','Revealing'),
				('redeemed','Complete'),
			],
			initial=['all'],
			widget=forms.SelectMultiple(
				attrs={'class':'form-control'}
			))

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(SortForm, self).__init__(*args, **kwargs)


class AskForm(forms.Form):
	question = forms.CharField(
			label='Question',
			# initial=notices.ASK_TEMPLATE,
			required=True,
			max_length=bm.MAX_QUESTION_LEN,
			widget=forms.Textarea(attrs={
				'class':'form-control',
				'style':'resize: none'}))
	down_payment = forms.DecimalField(
			label='Deposit',
			initial=Decimal(1.5),
			min_value=Decimal(0),
			required=True,
			decimal_places=18,
			max_digits=100,
			widget=forms.TextInput(attrs={
					'class':'form-control',
					# 'step':'0.5',
					}))
	denom = forms.ChoiceField(
			label='Denomination',
			required=True,
			choices=DENOM_OPTIONS,
			initial='ether',
			widget=forms.Select(attrs={'class':'form-control'}))
	# This is in seconds
	start_time = forms.IntegerField(
			label='Start Time',
			required=True)
	commit_period = forms.IntegerField(
			label='Commit Period (hours)',
			initial=24,
			required=True,
			min_value=1,
			widget=forms.TextInput(attrs={'class':'form-control'}))
	reveal_period = forms.IntegerField(
			label='Reveal Period (hours)',
			initial=24,
			required=True,
			min_value=1,
			widget=forms.TextInput(attrs={'class':'form-control'}))

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(AskForm, self).__init__(*args, **kwargs)


class TransferForm(forms.Form):
	transfer_amount = forms.DecimalField(
			label='Transfer Amount',
			initial=Decimal(1.5),
			min_value=Decimal(0),
			required=True,
			decimal_places=18,
			max_digits=100,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	denom = forms.ChoiceField(
			label='Denomination',
			required=True,
			choices=DENOM_OPTIONS,
			initial='ether',
			widget=forms.Select(attrs={'class':'form-control'}))
	recipient = forms.CharField(
			label='Recipient Address (hex)',
			required=True,
			max_length=42,
			min_length=40,
			widget=forms.TextInput(attrs={'class':'form-control'}))

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(TransferForm, self).__init__(*args, **kwargs)
