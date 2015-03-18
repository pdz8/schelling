from django.conf.urls import patterns, url
import ballots.views


urlpatterns = patterns('',

	# Main urls
	url(r'^ask/', ballots.views.ask, name='ask'),
	url(r'^explore/', ballots.views.explore, name='explore'),
	url(r'^hex/(0x)?(?P<address>[0-9a-fA-F]{40})/', 
			ballots.views.vote, name='hex'),
	url(r'^about/', ballots.views.about, name='about'),

	# Alternatives
	url(r'^create/', ballots.views.ask, name='create'),

	# Default index
	url(r'^$', ballots.views.explore),
)
