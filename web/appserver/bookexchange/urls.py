from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]

#reasoning for this file here
#https://docs.djangoproject.com/en/1.10/intro/tutorial01/
