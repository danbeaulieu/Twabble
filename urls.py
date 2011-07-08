from django.conf.urls.defaults import *
import os.path
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.conf import settings

## a comment to see if git works
MYMEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static'),

urlpatterns = patterns('',
    # Example:
    # (r'^Twabble/', include('Twabble.foo.urls')),
    (r'^/$', 'Twabble.games.views.index'),
    (r'^$', 'Twabble.games.views.index'), 
    (r'^logout/$', 'Twabble.games.views.logout_view'),
	(r'^startgame/$', 'Twabble.games.views.start'),
	(r'^g/$', 'Twabble.games.views.games'),
	(r'^g/(?P<game_id>\d+)/$', 'Twabble.games.views.game'),
	(r'^mygames/$', 'Twabble.games.views.mygames'),
	(r'^join/(?P<game_id>\d+)/$', 'Twabble.games.views.join'), 
    (r'^accounts/login/$', 'Twabble.games.views.login_prompt'),
    (r'^search/$', 'Twabble.games.views.search'),
    (r'^u/(?P<twuser_id>\d+)/(?P<twuser_name>.+)/$', 'Twabble.games.views.twuser'),
    (r'^m/(?P<membership_id>\d+)/(?P<membership_slug>.+)/$', 'Twabble.games.views.member_stats'),
    (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'games/about.html'}),
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)
urlpatterns += patterns('',
	url(r'^login/$', 'twitter_signin', name='login', prefix='Twabble.games.views'),
	url(r'^return/$', 'twitter_return', name='return', prefix='Twabble.games.views'), 
)

urlpatterns += patterns('django.views.static',
        (r'^static/(?P<path>.*)$', 'serve',
        {'document_root': settings.STATIC_ROOT})
)
