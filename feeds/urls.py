from django.conf.urls import url

from bootcamp.feeds import views

urlpatterns = [
    url(r'^$', views.feeds, name='feeds'),
    url(r'^post/$', views.post, name='post'),
    url(r'^like/$', views.like, name='like'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^load/$', views.load, name='load'),
    url(r'^check/$', views.check, name='check'),
    url(r'^load_new/$', views.load_new, name='load_new'),
    url(r'^update/$', views.update, name='update'),
    url(r'^track_comments/$', views.track_comments, name='track_comments'),
    url(r'^remove/$', views.remove, name='remove_feed'),
    url(r'^(\d+)/$', views.feed, name='feed'),
    url(r'^blog/$', views.blog, name='blog'),

    #url(r'^edit/(?P<pk>\d+)/$',views.EditComments.as_view(), name='edit_comments'),

    #url(r'^follow/(?<user_profile_id>[\d]+)/$', views.follow_user)

    #url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'views.toggle', name='toggle'),
    #url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'views.toggle', name='follow'),
   # url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'views.toggle', name='unfollow'),
]
