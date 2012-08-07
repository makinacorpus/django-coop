# WSGI config for {{ project_name }} project.

ALLDIRS = ['/home/admin/.virtualenvs/coop/lib/python2.7/site-packages']

# passing this variable to template context = ticket 18277
# TODO subclass the startproject command so we get this automatically

# the above directory depends on the location of your python installation.
# if using virtualenv, it will need to match your projects locale.
import os
import sys
import site

prev_sys_path = list(sys.path)

for directory in ALLDIRS:
    site.addsitedir(directory)
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
            sys.path[:0] = new_sys_path

sys.path.append('{{ project_directory }}')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coop_local.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

from django.core.wsgi import get_wsgi_application

try:
    from raven.contrib.django.middleware.wsgi import Sentry
    application = Sentry(get_wsgi_application())
except ImportError:
    application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
