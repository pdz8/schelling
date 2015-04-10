from decimal import *

from django import forms
from django.utils import timezone

import ballots.models as bm


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
	
	def __init__(self, choices, *args, **kwargs):
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
			label='Commit Period (minutes)',
			initial=1440,
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
	reveal_period = forms.IntegerField(
			label='Reveal Period (minutes)',
			initial=1440,
			required=True,
			min_value=1,
			widget=forms.NumberInput(attrs={'class':'form-control'}))
