from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^home', views.home, name='home'),
	url(r'^login', views.log_in, name='log_in'),
	url(r'^logout', views.log_out, name='log_out'),
	url(r'^register', views.register, name='register'),
	url(r'^sold', views.sold, name='sold'),
	url(r'^contact', views.contact, name='contact'),
	url(r'^listing_complete', views.listing_complete, name='listing_complete'),
	url(r'^finish_listing', views.finish_listing, name='finish_listing'),
	url(r'^list_new', views.list_new, name='list_new'),
	url(r'^search', views.search, name='search'),
	url(r'^results', views.results, name='results'),
]
