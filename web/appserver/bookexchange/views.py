from django.http import HttpResponse
from django.shortcuts import render
from .models import *

def get_listings_for_isbn(request):
	isbn_listings = []
	dict = request.GET
	
	if len(dict) == 0:
		return render(request, 'book_exchange/listing', isbn_listings)
		
	book_listings_data = []
	user_location = None
	
	if request.user.is_authenticated() and request.user.id:
		user_location = User.location # I don't know how to separate auth user and our User...
		book_listings_data = BookListing.objects.filter(location, dict)
	else:
		book_listings_data = BookListing.objects.filter(dict)
	
	for book_listing in book_listings_data:
		isbn_listings.append((book_listing.seller, book_listing.price, book_listing.condition))
	return render(request, 'book_exchange/listing', isbn_listings)
