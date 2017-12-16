from django.conf.urls import url

from bootcamp.follow import views

urlpatterns = [
    url(r'^$', views.user_detail, name='user_detail'),

]
