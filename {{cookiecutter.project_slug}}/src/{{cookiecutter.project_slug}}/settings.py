"""
Django settings for {{ cookiecutter.project_name }} project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import sys

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from os.path import dirname, join

from configurations import Configuration, values

BASE_DIR = dirname(dirname(dirname(__file__)))
DJANGO_DIR = join(BASE_DIR, 'src')


class Base(Configuration):
    # Build paths inside the project like this: join(BASE_DIR, "directory")
    STATICFILES_DIRS = [join(DJANGO_DIR, 'static')]
    STATIC_ROOT = join(DJANGO_DIR, 'static_root')
    STATIC_URL = '/static/'

    MEDIA_ROOT = join(DJANGO_DIR, 'media')
    MEDIA_URL = "/media/"

    # Use Django templates using the new Django 1.8 TEMPLATES settings
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                join(DJANGO_DIR, 'templates'),
                # insert more TEMPLATE_DIRS here
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                    # list if you haven't customized them:
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    'account.context_processors.account',
                    # `allauth` needs this from django
                    # 'django.template.context_processors.request',
                ],
            },
        },
    ]

    DEBUG = values.BooleanValue(False)

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
    SECRET_KEY = values.SecretValue()

    ALLOWED_HOSTS = []

    # Application definition

    DJANGO_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
    )

    THIRD_PARTY_APPS = (
        'django_extensions',
        'crispy_forms',
        'easy_thumbnails',
        {% if cookiecutter.use_sentry | lower == 'y' %}'raven.contrib.django.raven_compat', {% endif %}
        'account',
        'bootstrap3',
    )

    LOCAL_APPS = (
        'accounts',
    )

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        "account.middleware.LocaleMiddleware",
        "account.middleware.TimezoneMiddleware",
    )

    AUTHENTICATION_BACKENDS = (
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',
        'account.auth_backends.EmailAuthenticationBackend',

        # `allauth` specific authentication methods, such as login by e-mail
        # 'allauth.account.auth_backends.AuthenticationBackend',
    )

    ROOT_URLCONF = '{{ cookiecutter.project_slug }}.urls'

    WSGI_APPLICATION = '{{ cookiecutter.project_slug }}.wsgi.application'

    # MIGRATIONS CONFIGURATION
    # ------------------------------------------------------------------------------
    MIGRATION_MODULES = {
        'sites': 'contrib.sites.migrations'
    }

    ADMINS = (
        ("""{{cookiecutter.author_name}}""", '{{cookiecutter.email}}'),
    )

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
    MANAGERS = ADMINS

    # Database
    # https://docs.djangoproject.com/en/dev/ref/settings/#databases

    DATABASES = values.DatabaseURLValue()

    # Internationalization
    # https://docs.djangoproject.com/en/dev/topics/i18n/

    LANGUAGES = {{cookiecutter.available_languages}}

    LANGUAGE_CODE = values.Value('{{ cookiecutter.default_language }}')

    TIME_ZONE = values.Value('{{ cookiecutter.timezone }}')

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    ALLOWED_HOSTS = []

    # Crispy Form Theme - Bootstrap 3
    CRISPY_TEMPLATE_PACK = 'bootstrap3'

    # For Bootstrap 3, change error alert to 'danger'
    from django.contrib import messages
    MESSAGE_TAGS = {
        messages.ERROR: 'danger'
    }

    ACCOUNT_EMAIL_UNIQUE = True

    # Authentication Settings
    # AUTH_USER_MODEL = ''
    LOGIN_URL = reverse_lazy("account_login")

    THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
    {% if cookiecutter.use_sentry|lower == 'y' %}
    RAVEN_CONFIG = {
        'dsn': values.Value(environ_name='RAVEN_CONFIG_DNS'),
    }
    {% endif %}
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'normal': {
                'format': '[%(asctime)s] %(levelname)s %(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                          '%(thread)d %(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S',
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'normal',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': join(BASE_DIR, 'logs/errors.log'),
                'formatter': 'normal',
            },
            'general': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': join(BASE_DIR, 'logs/general.log'),
                'formatter': 'normal',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['console', 'error_file'],
                'level': 'WARNING',
                'propagate': True,
            },
        },
    }

    SITE_ID = values.IntegerValue(1)

    # Email sending configuration
    EMAIL_HOST = values.Value('localhost')
    EMAIL_PORT = values.IntegerValue(587)
    EMAIL_HOST_USER = values.Value()
    EMAIL_HOST_PASSWORD = values.Value()
    EMAIL_USE_TLS = values.BooleanValue(True)
    EMAIL_BACKEND = values.Value('django.core.mail.backends.smtp.EmailBackend')
    DEFAULT_FROM_EMAIL = values.Value('noreply@{{ cookiecutter.domain_name }}')


class Development(Base):
    DEBUG = values.BooleanValue(True)

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                join(DJANGO_DIR, 'templates'),
            ],
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    'account.context_processors.account',
                ],
                'debug': True,
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
                ],
            },
        },
    ]

    # Turn off debug while imported by Celery with a workaround
    # See http://stackoverflow.com/a/4806384
    if "celery" in sys.argv[0]:
        DEBUG = False

    INSTALLED_APPS = Base.INSTALLED_APPS + (
        'debug_toolbar.apps.DebugToolbarConfig',
        "autofixture",
    )

    ALLOWED_HOSTS = values.ListValue(['*'])

    EMAIL_BACKEND = values.Value(
        'django.core.mail.backends.console.EmailBackend')

    # Show thumbnail generation errors
    THUMBNAIL_DEBUG = True

    # Log everything to the logs directory at the top
    LOGFILE_ROOT = join(dirname(BASE_DIR), 'logs')


class Production(Base):
    DEBUG = values.BooleanValue(False)
    TEMPLATE_DEBUG = values.BooleanValue(False)

    ALLOWED_HOSTS = values.ListValue([])

    # Cache the templates in memory for speed-up
    loaders = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                join(DJANGO_DIR, 'templates'),
            ],
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    'account.context_processors.account',
                ],
                'debug': False,
                'loaders': loaders,
            },
        },
    ]

    # Log everything to the logs directory at the top
    LOGFILE_ROOT = join(dirname(BASE_DIR), 'logs')
