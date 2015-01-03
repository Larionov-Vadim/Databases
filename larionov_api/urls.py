from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'larionov_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^db/api/user/(?P<method>\S+)', 'larionov_api_app.views.user_view'),
    url(r'^db/api/forum/(?P<method>\S+)', 'larionov_api_app.views.forum_view'),
    url(r'^db/api/thread/(?P<method>\S+)', 'larionov_api_app.views.thread_view'),
    url(r'^db/api/post/(?P<method>\S+)', 'larionov_api_app.views.post_view'),
    url(r'^db/api/clear/', 'larionov_api_app.views.clear_view'),

    #url(r'^db/api/user/(?P<method>\S+)', 'larionov_api_app.views.user_view'),
    #url(r'^db/api/forum/(?P<method>\S+)', 'larionov_api_app.views.forum_view'),
    #url(r'^db/api/thread/(?P<method>\S+)', 'larionov_api_app.views.thread_view'),
    #url(r'^db/api/post/(?P<method>\S+)', 'larionov_api_app.views.post_view'),
    #url(r'^db/api/clear/', 'larionov_api_app.views.clear_view'),

    #url(r'$', 'larionov_api_app.views.hello'),
)