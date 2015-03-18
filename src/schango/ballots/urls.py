from django.conf.urls import patterns, url
import ballots.views


urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'schango.views.home', name='home'),
	# url(r'^blog/', include('blog.urls')),

	url(r'^create/', ballots.views.create, name='create'),
	url(r'^explore/', ballots.views.explore, name='explore'),
	url(r'^hex/(0x)?(?P<address>[0-9a-fA-F]{40})/', 
			ballots.views.vote, name='hex'),

	# Default index
	url(r'^$', ballots.views.explore),
)
