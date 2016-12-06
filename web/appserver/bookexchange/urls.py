from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^home', views.home, name='home'),
	url(r'^login', views.login, name='login'),
	url(r'^register', views.register, name='register'),
	url(r'^sold', views.sold, name='sold'),
	url(r'^list_new', views.list_new, name='list_new'),
	# url(r'^search/', views.search, name='search'),
    # url(r'^(?P<isbn>[0-9Xx]{10})/$', views.get_listing_for_isbn, name='listing'),
    # url(r'^(?P<isbn>[0-9Xx]{13})/$', views.get_listing_for_isbn, name='listing'),
]

#reasoning for this file here
#https://docs.djangoproject.com/en/1.10/intro/tutorial01/
