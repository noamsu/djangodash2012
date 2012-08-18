from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings
urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'djangodash.views.home', name='home'),
    url(r'^login$', 'djangodash.views.login', name='login'),
    url(r'^register$', 'djangodash.views.register', name='register'),
    url(r'^logout$', 'djangodash.views.logout', name='logout'),

    # Add a comment
    url(r'^add_comment$', 'djangodash.views.add_comment', name='add_comment'),

    # Thread page
	url(r'^thread/(?P<thread_id>.*)$', 'djangodash.views.thread', name='thread'),

    # Profile page
	url(r'^user/(?P<username>.*)$', 'djangodash.views.user_profile', name='user'),


	# Ajax urls
    url(r'^ajax/vote', 'djangodash.views.vote', name="vote"),

    # url(r'^djangodash/', include('djangodash.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Serve static files
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

)
