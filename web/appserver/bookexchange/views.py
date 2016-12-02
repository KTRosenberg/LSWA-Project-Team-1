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
	
		try:
			seller_profile = UserProfile.objects.get(user_id=request.user.id)
    	except UserProfile.DoesNotExist:
			return HttpResponse("Seller's user profile does not exist")
			
			
		# TODO
		# issue a call to the books API to retrieve title, author, edition
		
		isbn_13   = request.GET.get('isbn_13')
		price     = request.GET.get('price')
		condition = request.GET.get('condition')
		title = ....
		author = ....
		edition = ....
		
		book_listing = models.BookListing(
			isbn_13=isbn_13, 
			price=price, 
			condition=condition,
			seller=seller_profile,
			title=title,
			author=author,
			edition=edition 
		)
		
		# test whether a record for this isbn exists
		try:
			sales_total = IsbnSalesTotal.objects.get(isbn_13=isbn_13)
		except IsbnSalesTotal.DoesNotExist:
			sales_total = models.IsbnSalesTotal(
				isbn_13=isbn_13,
				copies_sold_NEW=0,
    			copies_sold_LIKE_NEW=0,
    			copies_sold_GOOD=0,
    			copies_sold_FAIR=0,
    			copies_sold_POOR=0,
    			total_sales_amount_NEW=0,
    			total_sales_amount_LIKE_NEW=0,
    			total_sales_amount_GOOD=0,
    			total_sales_amount_FAIR=0,
    			total_sales_amount_POOR=0,
				total_copies_sold_ALL=0
			)
					
		book_listing.save()
		sales_total.save()
		
		return HttpResponse("Success")
	else:
		return HttpResponse("Not authenticated")
		
##########################################################################################

def see_own_book_listings(request):
	if request.user.is_authenticated() and request.user.id:	
		try:
			seller_profile = UserProfile.objects.get(user_id=request.user.id)
		except UserProfile.DoesNotExist:
			return HttpResponse("Seller's user profile does not exist")	
					
		try:
			own_book_listings = BookListing.objects.filter(seller=seller_profile)
		except BookListing.DoesNotExist:
			return HttpResponse("Book listings do not exist for this user")
		
		return 	return render(request, 'book_exchange/personallistings', own_book_listings)
	else:
		return HttpResponse("Not authenticated")
		
##########################################################################################

def de_list_book(request):
	if request.user.is_authenticated() and request.user.id:
		try:
			seller_profile = UserProfile.objects.get(user_id=request.user.id)
		except UserProfile.DoesNotExist:
			return HttpResponse("Seller's user profile does not exist")
			
		try:
      		isbn_13 = request.GET.get("isbn_13") # somehow map the ISBN to the title for the email?
    	except KeyError:
			return HttpResponse("ISBN does not exist")
			
		try:
      		is_sold = request.GET.get("is_sold")
    	except KeyError:
			return HttpResponse("no such information available")
			
		# returns a list, so duplicates possible?
		try:
			book_listings = BookListing.objects.filter(seller=seller_profile, isbn_13=isbn_13)
		except BookListing.DoesNotExist:
			return HttpResponse("No such book listing to de-list")
		
		if len(book_listings) == 0:
			return HttpResponse("Nothing to de-list")

		book_to_delist = book_listings[0]
		if is_sold:
			# update sales total
			# if something fails here will we have to reverse all changes?
			try:
				sales_total = IsbnSalesTotal.objects.get(isbn_13=isbn_13)
			except IsbnSalesTotal.DoesNotExist:
				return HttpResponse("Sales total cannot be found, de-listing failed")
				
			condition = sales_total.condition
			price     = sales_total.price
			
			# TODO : make this more generic (non-hard coded in case options are changed
			if condition == IsbnSalesTotal.NEW:
				sales_total.copies_sold_NEW += 1
				sales_total.total_sales_amount_NEW += book_to_delist.price
			elif condition == IsbnSalesTotal.LIKE_NEW:
				sales_total.copies_sold_LIKE_NEW += 1
				sales_total.total_sales_amount_LIKE_NEW += book_to_delist.price
			elif condition == IsbnSalesTotal.GOOD:
				sales_total.copies_sold_GOOD += 1
				sales_total.total_sales_amount_GOOD += book_to_delist.price
			elif condition == IsbnSalesTotal.FAIR:
				sales_total.copies_sold_FAIR += 1
				sales_total.total_sales_amount_FAIR += book_to_delist.price
			elif condition == IsbnSalesTotal.POOR:
				sales_total.copies_sold_POOR += 1
				sales_total.total_sales_amount_POOR += book_to_delist.price
			else:
				return HttpResponse('Sales total error with "condition", de-listing failed')
			sales_total.total_copies_sold_ALL += 1

		# only delete if unsold or sold and updated successfully ?
		book_to_delist.delete()	
	else:
		return HttpResponse("Not authenticated")	


