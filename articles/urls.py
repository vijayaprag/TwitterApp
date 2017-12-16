from django.conf.urls import url

from bootcamp.articles import views
from bootcamp.articles.views import ArticleYearArchiveView

urlpatterns = [
    url(r'^$', views.articles, name='articles'),
    url(r'^write/$', views.CreateArticle.as_view(), name='write'),
    url(r'^preview/$', views.preview, name='preview'),
    url(r'^drafts/$', views.drafts, name='drafts'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^tag/(?P<tag_name>.+)/$', views.tag, name='tag'),
    url(r'^edit/(?P<pk>\d+)/$',
        views.EditArticle.as_view(), name='edit_article'),
    url(r'^(?P<slug>[-\w]+)/$', views.article, name='article'),

    url(r'^category/(?P<category_name>.+)/$', views.category, name='category'),


   #url(r'^like/$', views.like, name='like'),
   url(r'^(?P<year>[0-9]{4})/$',ArticleYearArchiveView.as_view(),name="article_year_archive"),

]
