"""
Django settings for schango project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8t%41d6#j2rkw(%bm4130o0x$!4_#n-x4q2^!(@(am%u0u6+cf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# TODO: Change this to final domain!
ALLOWED_HOSTS = ['.scoin.com']


# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'ballots',
	'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'schango.urls'

WSGI_APPLICATION = 'schango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

#####################
## Message passing ##
#####################

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
	message_constants.ERROR: 'danger',
}


#############################
## Facebook authentication ##
#############################

TEMPLATE_CONTEXT_PROCESSORS = (
	# Default
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.tz',
	'django.contrib.messages.context_processors.messages',

	# Social auth
	'social.apps.django_app.context_processors.backends',
	'social.apps.django_app.context_processors.login_redirect',

	# pdz8
	'ballots.context_processors.user_processor',
)

AUTHENTICATION_BACKENDS = (
	'social.backends.facebook.FacebookOAuth2',
	'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_FACEBOOK_KEY = '1565849607002326'
SOCIAL_AUTH_FACEBOOK_SECRET = 'dff1dea4cf9ecc112b7a3b8281255945'
SOCIAL_AUTH_FACEBOOK_SCOPE = []
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {}


#######################
## Ethereum settings ##
#######################

# TODO change all these
ENABLE_ETH = False
ADMIN_ADDRESS = 'e6389d124a71c6f5f671cbc0a5a6fb22aac80ff4'
ADMIN_SECRET = '99d0ca395a634c3d8e7b7f1893cf87fd71c66daa654271ee22fdb541be262587'
VOTER_POOL_ADDRESS = 'b7a11e17aecf399a3821d006ded0df750adcfbcc'


