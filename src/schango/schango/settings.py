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
	# message_constants.ERROR: 'danger',
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

SOCIAL_AUTH_FACEBOOK_SCOPE = []
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {}

# These are DEFAULT VALUES
# Override in local_settings.py
SOCIAL_AUTH_FACEBOOK_KEY = '1571810896406197' # SCOIN-Test1
SOCIAL_AUTH_FACEBOOK_SECRET = '1c53e7351e654dc6313b9f22589240e2' # SCOIN-Test1


#######################
## Ethereum settings ##
#######################

# These are DEFAULT VALUES
# Override in local_settings.py
ENABLE_ETH = False
ADMIN_ADDRESS = '1d6f390b1d4acfc2b8de0de51ecec83fa066f790'
ADMIN_SECRET = '74b12683b0c444efe79aa1e480c624f7dc4772f4c14ac2bd783b0ed8c4a197f6'
VOTER_POOL_ADDRESS = '320bbe4c03e3277cbeb256e875885c7c69b054b9'
ETHD_HOST = '127.0.0.1'


####################
## Local settings ##
####################
# This needs to be at the bottom of the settings file!

try:
	from local_settings import *
except:
	pass
