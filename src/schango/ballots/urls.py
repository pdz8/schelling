from django.conf.urls import patterns, url
import ballots.views


urlpatterns = patterns('',

	# Main urls
	url(r'^ask/', ballots.views.ask, name='ask'),
	url(r'^explore/', ballots.views.explore, name='explore'),
	url(r'^hex/(0x)?(?P<address>[0-9a-fA-F]{40})/', 
			ballots.views.vote, name='hex'),
	url(r'^about/', ballots.views.about, name='about'),
	url(r'^account/', ballots.views.account, name='account'),
	url(r'^logout/', ballots.views.logout, name='logout'),

	# Alternatives
	url(r'^create/', ballots.views.ask, name='create'),
	url(r'^vote/', ballots.views.vote, name='vote'),

	# Testing/debugging/sandbox
	url(r'^debug/', ballots.views.debug, name='debug'),

	# Default index
	url(r'^$', ballots.views.explore),
)
