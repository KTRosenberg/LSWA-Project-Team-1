from django.http import HttpResponse
from django.shortcuts import render
from .models import *
import django.core.mail

##########################################################################################

def get_listing_for_isbn(request):
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
			return HttpResponse("User profile does not exist")	
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

##########################################################################################
	
def send_purchase_request_email(request):

	if request.user.is_authenticated() and request.user.id:
	
		try:
      		inquirer_profile = UserProfile.objects.get(user_id=request.user.id)
    	except UserProfile.DoesNotExist:
			return HttpResponse("Inquirer's user profile does not exist")
			
		try:
      		seller_profile = request.GET.get("seller")
    	except KeyError:
			return HttpResponse("Seller's user profile does not exist")
			
		try:
      		isbn_13 = request.GET.get("isbn_13") # somehow map the ISBN to the title for the email?
    	except KeyError:
			return HttpResponse("ISBN does not exist")
			
		try:
			book_title = BookListing.objects.get(isbn_13=isbn_13).title
		except BookListing.DoesNotExist:
			return HttpResponse("No book title matching ISBN exists")	

		send_mail(
			"Book sale inquiry", 
			"%s would like to buy your copy of %s. Please email them at %s." % (inquirer_profile.name, book_title, inquirer_profile.email,),
			inquirer_profile.email, # but this is an email field--can I do this?
			[seller_profile.email],
			auth_user=request.user
		)

	else:
		return HttpResponse("Not authenticated")
		
##########################################################################################

def list_a_book(request):
	if request.user.is_authenticated() and request.user.id:
		# TODO
		# issue a call to the books API to retrieve title, author, edition
		
		isbn_13   = request.GET.get('isbn_13')
		price     = request.GET.get('price')
		condition = request.GET.get('condition')
		title = ....
		author = ....
		edition = ....
		
		try
			seller_profile = UserProfile.objects.get(user_id=request.user.id)
    	except UserProfile.DoesNotExist:
			return HttpResponse("Seller's user profile does not exist")
			
		book_listing = models.BookListing(
			isbn_13=isbn_13, 
			price=price, 
			condition=condition,
			seller=seller_profile,
			title=title,
			author=author,
			edition=edition 
		)
		book_listing.save()
		
		return HttpResponse("Success")
	else:
		return HttpResponse("Not authenticated")

