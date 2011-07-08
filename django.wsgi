import os
import sys
sys.path.append('/home/dan/django_projects')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Twabble.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

