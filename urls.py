from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from bootcamp.activities import views as activities_views
from bootcamp.authentication import views as bootcamp_auth_views
from bootcamp.core import views as core_views
from bootcamp.search import views as search_views
from django.contrib import admin
admin.autodiscover()
#from bootcamp.follow import views
#from bootcamp.core import views
#from pusherchat import views


urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^login', auth_views.login, {'template_name': 'core/cover.html'},
        name='login'),
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/$', bootcamp_auth_views.signup, name='signup'),
    url(r'^settings/$', core_views.settings, name='settings'),
    url(r'^settings/picture/$', core_views.picture, name='picture'),
    url(r'^settings/upload_picture/$', core_views.upload_picture,
        name='upload_picture'),
    url(r'^settings/save_uploaded_picture/$', core_views.save_uploaded_picture,
        name='save_uploaded_picture'),

    url(r'^settings/coverpicture/$', core_views.coverpicture, name='coverpicture'),
    url(r'^settings/cover_upload_picture/$', core_views.cover_upload_picture,
        name='cover_upload_picture'),
    url(r'^settings/save_cover_uploaded_picture/$', core_views.save_cover_uploaded_picture,
        name='save_cover_uploaded_picture'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^settings/password/$', core_views.password, name='password'),
    url(r'^network/$', core_views.network, name='network'),
    url(r'^feeds/', include('bootcamp.feeds.urls')),
    url(r'^questions/', include('bootcamp.questions.urls')),
    url(r'^articles/', include('bootcamp.articles.urls')),
    url(r'^messages/', include('bootcamp.messenger.urls')),
    url(r'^notifications/$', activities_views.notifications,
        name='notifications'),
    url(r'^notifications/last/$', activities_views.last_notifications,
        name='last_notifications'),
    url(r'^notifications/check/$', activities_views.check_notifications,
        name='check_notifications'),
    url(r'^search/$', search_views.search, name='search'),
    url(r'^contact/$', core_views.contact, name='contact'),
    url(r'^email/$', core_views.email, name='email'),
    url(r'^thanks/$', core_views.thanks, name='thanks'),
    url(r'^thanksinvite/$', core_views.thanksinvite, name='thanksinvite'),
    url(r'^thankyou/$', core_views.thankyou, name='thankyou'),
    url(r'^thankyouinvite/$', core_views.thankyouinvite, name='thankyouinvite'),
    #url(r'^archives/$', core_views.archives, name='archives'),
    url(r'^trending/$', core_views.trending, name='trending'),
    url(r'^news/$', core_views.news, name='news'),
     url(r'^newsfeed/$', core_views.newsfeed, name='newsfeed'),
    url(r'^postcrawler/$', core_views.postcrawler, name='postcrawler'),
    url(r'^searchcrawler/$', core_views.searchcrawler, name='searchcrawler'),
    url(r'^follow/(?P<user_profile_id>[^/]+)/$', core_views.follow_user, name='profile'),

    url(r'^chat/$', core_views.chat, name='chat'),
    #url(r'^ajax/chat/$', core_views.broadcast, name='broadcast'),

    url(r'^(?P<username>[^/]+)/$', core_views.profile, name='profile'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),




    #url(r'^follow/', include('bootcamp.follow.urls')),
    #url(r'^admin/', admin.site.urls),
    #url(r'^settings/forgotpassword/$', core_views.forgotpassword, name='forgotpassword'),




]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
