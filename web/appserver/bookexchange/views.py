from django.http import HttpResponse
from django.shortcuts import render
from .models import *

def get_listings_for_isbn(request):
	isbn_listings = []
		
	if len(arg_dict) == 0:
		return render(request, 'book_exchange/listing', isbn_listings)
		
	book_listings_data = []
	user_location = None
	
	valid_filter_dict = get_valid_filter_dict(request.GET)
	
	if valid_dict == None:
		return render(request, 'book_exchange/listing', isbn_listings)
	
	if request.user.is_authenticated() and request.user.id:
		valid_dict['location'] = ...
		user_location = User.location # I don't know how to separate auth user and our User...
		
		# somehow add the location to the dictionary so the filter just receives the dict?
		book_listings_data = BookListing.objects.filter(location, arg_dict)
	else:
		book_listings_data = BookListing.objects.filter(arg_dict)
	
	for book_listing in book_listings_data:
		isbn_listings.append((book_listing.seller, book_listing.price, book_listing.condition))
	return render(request, 'book_exchange/listing', isbn_listings)

def get_valid_filter_dict(input_dict):
	# Title (optional), Author (optional), ISBN (optional) (must specify at least one)
	has_enough_args = False
	valid_arg_list = ['title', 'author', 'isbn_13']
	valid_filter_dict = {}
	
	for valid_arg in valid_arg_list:
		if valid_arg in input_dict:
			valid_filter_dict[valid_arg] = input_dict[valid_arg]
			
	return valid_filter_dict
