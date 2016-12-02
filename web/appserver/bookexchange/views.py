from django.http import HttpResponse
from django.shortcuts import render
from .models import *

def get_isbn_listing_view(request):
	isbn_listing_info_out = []
		
	if len(arg_dict) == 0:
		return HttpResponse("Invalid number of arguments")
			
	valid_filter_dict = get_valid_filter_dict(request.GET)
	
	if len(valid_filter_dict) == 0:
		return HttpResponse("Invalid arguments provided")
		
	if request.user.is_authenticated() and request.user.id:
		try:
      		user_profile = UserProfile.objects.get(user_id=request.user.id) # ??
    	except UserProfile.DoesNotExist:
			return HttpResponse("Invalid user profile")	
		valid_dict['location'] = user_profile.location
		
	book_listings = BookListing.objects.filter(**valid_filter_dictarg_dict)
	
	for book_listing in book_listings:
		isbn_listing_info_out.append((book_listing.seller, book_listing.price, book_listing.condition))
		
	return render(request, 'book_exchange/listing', isbn_listing_info_out)

def get_valid_filter_dict(input_dict):
	# Title (optional), Author (optional), ISBN (optional) (must specify at least one)
	valid_arg_list = ['title', 'author', 'isbn_13']
	valid_filter_dict = {}
	
	for valid_arg in valid_arg_list:
		if valid_arg in input_dict:
			valid_filter_dict[valid_arg] = input_dict[valid_arg]
			
	return valid_filter_dict
