from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

	# Social authentication
	url('', include('social.apps.django_app.urls', namespace='social')),

	# Admin site
	url(r'^admin/', include(admin.site.urls)),

	# Apps
	url(r'^ballots/', include('ballots.urls', namespace='ballots')),

	# Default fall-through
	url(r'', include('ballots.urls')),
)

