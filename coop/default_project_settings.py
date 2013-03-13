# -*- coding:utf-8 -*-
import os
from coop_local.settings import PROJECT_PATH, PROJECT_NAME
from ionyweb import get_ionyweb_path

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-FR'

from multisite import SiteID
SITE_ID = SiteID(default=1)
COOP_USE_SITES = False


USE_I18N = True
USE_L10N = True

DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET = 'utf-8'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

USE_TZ = False

# Upload directory
MEDIA_ROOT = os.path.abspath(PROJECT_PATH + '/media/')
MEDIA_URL = '/media/'

# Static files
STATIC_ROOT = os.path.abspath(PROJECT_PATH + '/static_collected/')
STATIC_URL = '/static/'

# compat fix ?
ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"


import admin_tools
ADMIN_TOOLS_PATH = os.path.dirname(os.path.abspath(admin_tools.__file__))


STATICFILES_DIRS = [
    os.path.abspath(ADMIN_TOOLS_PATH + '/media/'),
    os.path.join(get_ionyweb_path(), 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'ionyweb.loaders.layouts_finders.StaticFinder',
    'ionyweb.loaders.themes_finders.StaticFinder',
]


TEMPLATE_DIRS = [
    os.path.abspath(PROJECT_PATH + '/coop_local/templates/')
]

TEMPLATE_LOADERS = [
    'multisite.template_loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
    'apptemplates.Loader',
    'ionyweb.loaders.layouts_templates.Loader',
    'ionyweb.loaders.themes_templates.Loader',
]

MIDDLEWARE_CLASSES = [
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'multisite.middleware.DynamicSiteMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django_webid.auth.middleware.WEBIDAuthMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'coop.utils.middleware.CORSMiddleware',
#    'pagination.middleware.PaginationMiddleware',
    'ionyweb.website.middleware.ProvideWebSiteMiddleware',
    'ionyweb.website.middleware.PreamptiveWebSiteMiddleware',      
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'coop.context_processors.current_site',
    'preferences.context_processors.preferences_cp',
    'ionyweb.context_processors.user_rights',
    'ionyweb.context_processors.admin_page_data',
    'ionyweb.context_processors.site_settings',    
    'django.core.context_processors.csrf',
    'sekizai.context_processors.sekizai',
]

ROOT_URLCONF = 'coop_local.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coop_local.wsgi.application'

CACHE_MULTISITE_ALIAS = 'multisite'

# Cache middelware must be enabled above
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'memcached': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        'LOCATION': 'unix:/tmp/memcached.sock',
    },
    'multisite': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
    }
}

CACHE_MIDDLEWARE_ALIAS = 'memcached'
CACHE_MIDDLEWARE_SECONDS = 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_NAME


# The view function or class-based view that django-multisite will
# use when it cannot match the hostname with a Site. This can be
# the name of the function or the function itself.
# Default: None
MULTISITE_FALLBACK = 'django.views.generic.base.RedirectView'

INSTALLED_APPS = [

    # admin tools
    'admintools_bootstrap',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    # django contribs
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'django.contrib.admindocs', # ramène sa traduction de Tags "Étiquettes"...
    'django.contrib.gis',
    'django.contrib.comments',
    # 'djgeojson',

    # other 3rd parties
    'south',
    'django_extensions',
    'extended_choices',
    'floppyforms',
    # 'haystack',
    # 'haystack_fr',
    #'oembed',
    'chosen',
    'sorl.thumbnail',
    'tinymce',
    'autoslug',
    'slugify',
    'forms_builder.forms',
    'preferences',
    'apptemplates',
    'scanredirect',
    'multisite',
    'selectable',


    # WebID
    #'django_webid.provider',
    #'django_webid.auth',

    # coop apps
    'coop_tag',

    # 'feincms',  # for their MPTT tree editor, not synced
    'coop',  # override feincms tree editor template
    'coop.link',
    'coop.prefs',
    'coop.org',
    'coop.person',
    'coop.ui',
    'coop.rdf',

    'coop_geo',

    # PuSH
    'django_rq',
    'subhub',
    'django_push.subscriber',
    #'uriredirect',

    # coop_cms
    #'djaloha',
    #'coop_cms',
    #'coop_cms.apps.rss_sync',
    #'colorbox',
    #'coop_bar',
#    'pagination',

    #ionyweb
    'ionyweb',

    
    'django.contrib.sitemaps',
    'grappelli',
    'django.contrib.admindocs',
    'mptt',
    'sekizai',
    'djangorestframework',
    'less',
    
    'ionyweb.administration',
    'ionyweb.authentication',
    'ionyweb.design',
    'ionyweb.file_manager',
    'ionyweb.website',
    'ionyweb.page',
    'ionyweb.plugin',

    # Apps
    'ionyweb.page_app.page_text',
    'ionyweb.page_app.page_blog',
    'ionyweb.page_app.page_redirect',
    'ionyweb.page_app.page_agenda',
    'ionyweb.page_app.page_book',
    'ionyweb.page_app.page_gallery_images',
    'ionyweb.page_app.page_sitemap',
    'promess84_ionyweb.page_members',
    'promess84_ionyweb.page_coop_agenda',
    
    # Plugins
    'ionyweb.plugin_app.plugin_text',
    'ionyweb.plugin_app.plugin_image',
    'ionyweb.plugin_app.plugin_website_title',
    'ionyweb.plugin_app.plugin_video',
    'ionyweb.plugin_app.plugin_map',
    'ionyweb.plugin_app.plugin_links_list',
    'ionyweb.plugin_app.plugin_blog_entries_list',
    'ionyweb.plugin_app.plugin_contact',
    'ionyweb.plugin_app.plugin_fb_likebox',
    'ionyweb.plugin_app.plugin_breadcrumb',
    'promess84_ionyweb.plugin_members',
    'ionyweb.plugin_app.plugin_slideshow',    
]

COOP_BAR_MODULES = [
    'coop.coop_bar_cfg',
    ]

AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

TAGGER_TAG_MODEL = 'coop_local.models.Tag'
TAGGER_TAGGEDITEM_MODEL = 'coop_local.models.TaggedItem'
TAGGER_FKEY_NAME = 'coop_local.Tag'

THUMBNAIL_FORMAT = 'PNG'
ADMIN_THUMBS_SIZE = '60x60'

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'relative_urls': False,
    'width': '617px', 'height': '220px',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1': 'bold,italic,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,|,link,unlink,|,code',
    'theme_advanced_buttons2': '', 'theme_advanced_buttons3': ''
    }

#COOP_NEWLETTER_ITEM_CLASSES = ['article']

#COOP_CMS_ARTICLE_CLASS = 'coop_local.models.Article'
#COOP_CMS_ARTICLE_FORM = 'coop.forms.ArticleForm'
#COOP_CMS_ARTICLE_LOGO_SIZE = '600'


#COOP_CMS_NAVTREE_CLASS = 'coop_local.NavTree'

# You need to declare the app here to be able to select models from navigable types in coop-cms
#COOP_CMS_CONTENT_APPS = ('coop_local', 'coop_tag', 'coop_geo', 'coop_cms', 'forms')

#DJALOHA_LINK_MODELS = (
#        'coop_local.Article',
#        'coop_cms.ArticleCategory',
#        'coop_local.Organization',
#        'coop_local.OrganizationCategory',
#        'coop_local.Event',
#        )



# COOP_CMS_ARTICLE_TEMPLATES = 'coop_local.get_article_templates' # marche plus ?

#COOP_CMS_ARTICLE_TEMPLATES = [
#    ('coop_cms/article.html', 'Standard'),
#    ('coop_cms/article_nologo.html', 'Sans logo'),
#]


SKIP_DJALOHA_JQUERY = True

FORMS_BUILDER_USE_SITES = False


ADMIN_TOOLS_MENU = 'coop.ui.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'coop.ui.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'coop.ui.dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_THEMING_CSS = 'css/coop_bootstrap_theming.css'


AUTHENTICATION_BACKENDS = [
    #'django_webid.auth.backends.WEBIDAuthBackend',
    #'coop_cms.perms_backends.ArticlePermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PROFILE_MODULE = 'coop_local.Person'

# projection used in database
COOP_GEO_EPSG_PROJECTION = 4326  # WGS84

COOP_GEO_BOUNDING_BOX = []
COOP_GEO_REGION = LANGUAGE_CODE[:2]



#
# WebID Options
#

WEBIDAUTH_USE_COOKIE = True

# The following lines set the local user creation callback.
# All the info from the remote profile is accessible from
# the request.webidinfo object (see documentation).


def createusercb(req):
    from coop.webid.utils import build_coop_user
    return build_coop_user(req)

WEBIDAUTH_CREATE_USER_CALLBACK = createusercb

WEBIDPROVIDER_SKIP_PROFILE_INIT = True

# Uncomment the following lines if you want to specify
# a custom callback for the assigment of the WebIDUris.
# If this callback is not specified, provider will look for
# a webidprovider-webid_uri urlpattern and will try to
# reverse it passing the webiduser instance.

#def webidcb(webiduser):
#    "avoids circular import"
#    from coop.webid.utils import custom_webid_uri
#    return custom_webid_uri(webiduser)
#WEBIDPROVIDER_WEBIDURI_CALLBACK = webidcb


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simplest': {
            'format': '%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },

    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console-dumb': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simplest'
        },

        # access denied problem on prod env.... to be check
        #  'file_subhub': {  # define and name a handler
        #     'level': 'DEBUG',
        #     'formatter': 'simple',
        #     'class': 'logging.handlers.WatchedFileHandler',  # set the logging class to log to a file
        #     'filename': os.path.abspath(PROJECT_PATH + '/logs/subhub.log')  # log file
        # },
        #  'file_rqworker': {  # define and name a handler
        #     'level': 'DEBUG',
        #     'formatter': 'simple',
        #     'class': 'logging.handlers.WatchedFileHandler',  # set the logging class to log to a file
        #     'filename': os.path.abspath(PROJECT_PATH + '/logs/rq.log')  # log file
        # },


    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # 'subhub.maintenance': {
        #     'handlers': ['console'],
        #     'level': 'ERROR'
        # },
        # 'subhub.distribution.process': {
        #     'handlers': ['console'],
        #     'level': 'ERROR'

        # },
        'worker': {
            'handlers': ['console'],
            'level': 'DEBUG'

        },
        'coop': {
            'handlers': ['console-dumb'],
            'level': 'DEBUG',
        },
    },

}

# Autocompletion
SELECTABLE_MAX_LIMIT = 100


# import default app settings from django-coop app

try:
    from coop.settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find settings.py file from django-coop")

    
# import ionyweb settings

#try:
#    from ionyweb.settings import *
#except ImportError, exp:
#    raise ImproperlyConfigured("Unable to find settings.py file from ionyweb")

from ionyweb import get_ionyweb_path

#LAYOUTS_DEFAULT_PATH = 'layouts'
#LAYOUTS_DIRS = (
#    os.path.join(get_ionyweb_path(), 'contrib', LAYOUTS_DEFAULT_PATH),
#)

URLCONF_WEBSITE_ADMIN = u'ionyweb.administration.urls'

LAYOUTS_DEFAULT_PATH = 'layouts'
LAYOUTS_DIRS = (
    PROJECT_PATH + '/promess84_ionyweb/layouts',
)
THEMES_DEFAULT_PATH = 'themes'
THEMES_DIRS = (
   PROJECT_PATH + '/promess84_ionyweb/themes',
)   

SITE_NAME = "promess84"

TINYMCE_JS_URL = os.path.join(STATIC_URL, "tiny_mce/tiny_mce_src.js")
TINYMCE_JS_ROOT = os.path.join(get_ionyweb_path(), 'static', "tiny_mce")

TINYMCE_COMPRESSOR = True
TINYMCE_SPELLCHECKER = True
TINYMCE_FILEBROWSER = False
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,filemanager,paste,searchreplace,inlinepopups",
    'theme': "advanced",
    'theme_advanced_buttons1' : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontsizeselect,|,forecolor,backcolor,|,bullist,numlist,|,outdent,indent,|,sub,sup,|,charmap,emotions,separator,forecolor,backcolor",
    'theme_advanced_buttons2' : "pastetext,pasteword,selectall,|,undo,redo,|,link,unlink,anchor,image,filemanager,code,|,tablecontrols,|,fullscreen",
    'theme_advanced_buttons3' : "",
    'relative_urls': False
}


#----------------------
# RENDERING PAGE ENGINE
#----------------------
RESTRICTED_THEMES = []

SLUG_PLACEHOLDER = 'placeholder'
SLUG_PLUGIN = 'plugin-relation'
SLUG_APP = 'app'
SLUG_CONTENT = 'content'
SLUG_DEFAULT = 'default'
SLUG_CLIPBOARD = 'clipboard'
SLUG_LAYOUT = 'layout'
SLUG_SEP = '-'

HTML_ID_PLACEHOLDER = '%s%s%s' % (SLUG_SEP, SLUG_PLACEHOLDER, SLUG_SEP)
HTML_ID_PLACEHOLDER_CONTENT = '%s%s' % (SLUG_CONTENT, HTML_ID_PLACEHOLDER)
HTML_ID_PLACEHOLDER_DEFAULT = '%s%s%s' % (SLUG_DEFAULT, SLUG_SEP, SLUG_PLACEHOLDER)
HTML_ID_PLACEHOLDER_CLIPBOARD = '%s%s%s' % (SLUG_CLIPBOARD, SLUG_SEP, SLUG_PLACEHOLDER)
HTML_ID_APP = '%s%s' % (SLUG_APP, SLUG_SEP)
HTML_ID_PLUGIN = '%s%s' % (SLUG_PLUGIN, SLUG_SEP)
HTML_ID_LAYOUT = '%s%s' % (SLUG_LAYOUT, SLUG_SEP)
HTML_ID_NAV = 'nav'

TEMPLATE_PLACEHOLDER_DEFAULT = 'layout/placeholder-default.html'
TEMPLATE_PLACEHOLDER_CLIPBOARD = 'layout/clipboard.html'
TEMPLATE_PLACEHOLDER = 'layout/placeholder.html'
TEMPLATE_APP = 'layout/placeholder-app.html'
TEMPLATE_PLUGIN = 'layout/plugin.html'
TEMPLATE_NAV_DEFAULT = 'navigation.html'
TEMPLATE_MAINTENANCE_DEFAULT = 'maintenance.html'
TEMPLATE_THEME_FILE_DEFAULT = 'index.html'
LAYOUT_DEFAULT = '100'

#------------------
# PAGE APP URL CONF
#------------------
SLUG_MIN_SIZE = 4
URL_PAGE_APP_SEP = u'p'
URL_ADMIN_SEP = u'wa'

ACTION_ADMIN_LIST_SUFFIX = '_list'
ACTION_ADMIN_ORDER_SLUG = '_order'
ADMIN_THEME = 'dark' # 'snow' || 'dark' || ... Will import ionyweb_admin_***.less

SITEMAP_INDEX = False

# ----------------
# PLUGINS SETTINGS
# ----------------
BREADCRUMB_PLUGIN = 'ionyweb.plugin_app.plugin_breadcrumb'
BREADCRUMB_OBJECT_TITLE = 'breadcrumb_object_title'

INPUT_FORMATS = ['%d/%m/%Y %H:%M', '%d-%m-%Y %H:%M']

# ---------------
# WEBSITE DOMAINS
# ---------------
RESTRICTED_DOMAINS = []

# ------------
# FILE MANAGER
# ------------
EXTENSIONS = {
    'Folder': [''],
    'Image': ['jpg','jpeg','gif','png'],
    'Audio': ['mpeg'],
    'Document': ['pdf','doc','xls','odt', 'ods', 'rtf','txt','csv'],
    'Archive': ['zip', 'rar', 'tar', 'tar.gz', '7z'],
    'Others': [],
    #'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    #'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
}
DISPLAY_MODE = (
    (u"I", u"Icons"),
    (u"D", u"Details"),
    (u"L", u"Lists"),
)

VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
    'croppedthumbnail': {'verbose_name': 'Cropped Thumbnail (300x200px)', 'width': 300, 'height': 200, 'opts': 'crop upscale'},
    'croppedthumb': {'verbose_name': 'Cropped Thumbnail (140x100px)', 'width': 140, 'height': 100, 'opts': 'crop upscale'},
    'croppedbig': {'verbose_name': 'Cropped big (450x323)', 'width': '', 'height': 323, 'opts': 'crop upscale'},
}

ADMIN_THUMBNAIL = 'admin_thumbnail'
VERSION_QUALITY = 90
IMAGE_MAXBLOCK = 1024*1024
FILE_MANAGER_QUOTA = "1073741824" #1024^3b = 1Gb

DOMAIN_NAME = "localhost:8000"










