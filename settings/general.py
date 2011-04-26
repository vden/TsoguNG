# -*- coding: utf-8 -*-
# Django settings for tsogung project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('Webmaster', 'scailer@tsogu.ru'),
)

MANAGERS = ADMINS
EMAIL_HOST = "217.116.51.45"
EMAIL_PORT = 25

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
SPHINX_SERVER = "www.tsogu.ru"
SPHINX_PORT = 3312
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

TIME_ZONE = 'Asia/Yekaterinburg'
LANGUAGE_CODE = 'ru-ru'
SITE_ID = 1
USE_I18N = True
SESSION_COOKIE_NAME = 'tsoguSessionId'

LOGIN_URL_REDIRECT = "/action/workspace"
working_dir = os.path.dirname(__file__)
working_dir = '/'.join(working_dir.split('/')[:-1])
MEDIA_ROOT = working_dir + '/media/'
PHOTOS_ROOT = MEDIA_ROOT + 'photos/'
MEDIA_URL = '/media/'
PHOTOS_URL = MEDIA_URL + 'photos/'
FILE_ROOT = MEDIA_ROOT + 'files/'
THUMBNAIL_BASEDIR = 'photos'
FILE_URL = MEDIA_URL + 'files/'
ADMIN_MEDIA_PREFIX = '/adminmedia/'
ADMIN_MEDIA_ROOT = '/usr/lib/python2.6/site-packages/django/contrib/admin/media/'
CSS_ROOT = MEDIA_ROOT + "/css/"
JS_ROOT = MEDIA_ROOT + "/js/"
MERGED_FILES = MEDIA_ROOT + "/merged/"


CUSTOM_TEMPLATES = working_dir + "/core/templates/custom/"

BANNERS_ROOT = MEDIA_ROOT + "/img/banners/"
BANNERS_URL = MEDIA_URL + "img/banners/"

SECRET_KEY = '72#v8&im9l$9l!=&k4=q0#h#931j11w!q@%cj38!ga&@%xa=7c'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.cache.CacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'tsogung.middleware.messages.ExceptionRender',
#    'django.middleware.cache.FetchFromCacheMiddleware',
     'core.middleware.threadlocals.ThreadLocals',
     'core.middleware.environment.ThreadLocals',
#    'middleware.threadlocals.ThreadLocals',
    'core.middleware.profiler.ProfileMiddleware',
    'core.middleware.disablecsrf.disableCSRF',
#    'profiling.middleware.ProfileMiddleware',
)

CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'tsoguNG'

ROOT_URLCONF = 'tsogung.urls'

TEMPLATE_DIRS = (
	working_dir + '/core/templates/',
)

FIXTURE_DIRS = (working_dir + '/fixture/',)

INSTALLED_APPS = (
	'tsogung.core',
	'tsogung.pytils',
	'tsogung.banners',
	'tsogung.tinymce',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'userprofile',
	'django_extensions',
	'tsogung.rights',
	'tsogu_comments',
	'sorl.thumbnail',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.core.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.request",
)


if False:
	INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
	DEBUG_TOOLBAR_PANELS = (
		#'debug_toolbar.panels.version.VersionDebugPanel', # убрать. только место занимает.
		'debug_toolbar.panels.timer.TimerDebugPanel',
		'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
		'debug_toolbar.panels.headers.HeaderDebugPanel',
		'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
		'debug_toolbar.panels.template.TemplateDebugPanel',
		'debug_toolbar.panels.sql.SQLDebugPanel',
#		'debug_toolbar.panels.cache.CacheDebugPanel',
		'debug_toolbar.panels.logger.LoggingPanel',
	)
	MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

	DEBUG_TOOLBAR_CONFIG = {
		'EXCLUDE_URLS': ('/admin',), # не работает, но в разработке есть...
		'INTERCEPT_REDIRECTS': False,
	}

	INTERNAL_IPS = ('127.0.0.1',)

COMMON_MEDIA_URL = 'http://std.tsogu.ru/media/'
AUTH_PROFILE_MODULE = 'userprofile.Profile'
EXTENSIONS_MEDIA_ROOT = ''

UNIV_DB = ''
UNIV_USER = ''
UNIV_PASSWD = ''
UNIV_HOST = ''
UNIV_PORT = ''

SEND_EXCEPTIONS = False
LOG_EXCEPTIONS = False
EMAIL_SUBJECT_PREFIX = '[TSOGU NG CMS] '
EDITOR_EMAIL = 'webmaster@tsogu.ru'

UUID_NAMESPACE_FOR_EMAIL_CONFIRM = '0dbd5f90-77b7-58a5-9f0b-dab5fe4c4bf9' # Don't change it !!!
EDUCON_URL = "http://educon.tsogu.ru:8081/student_status_confirm.php/"
