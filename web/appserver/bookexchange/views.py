from django.contrib.auth.models import User
from decimal import Decimal
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from .api import get_book_by_isbn, get_books_by_author_and_title
from django.core.cache import cache

# views:
# landing page / log in
# register
# user home page - see your books
# list a book for sale
# search for a book for sale - isbn, author/title
# contact seller (email)
# seller: de-list a book for sale

def send_email(seller, book, user):
	message = """Hi %s!

	%s is interested in purchasing this book from you:

	Title: %s
	Author: %s
	ISBN: %s
	Edition: %s
	Condition: %s
	Price: %s

	You can reach %s at %s.

	-LSWA Book Exchange


	(Please do not reply to this email)""" % (seller.username, user.username,
	                                          book.title, book.author, book.isbn_13,
	                                          book.cover_type, book.condition,
	                                          book.price, user.username, user.email)

	send_mail(
	    user.username + ' wants to buy your book!',
	    message,
	    'LSWABookExchange@nyu.edu',
	    [seller.email],
	    fail_silently=False,
	)

def contact(request):
	if request.user.is_authenticated():
		bookId = request.POST.get('bookId')
		book = BookListing.objects.get(id=bookId)#.select_related('seller')
		seller = book.seller
		send_email(seller, book, request.user)
		return render(request, 'contact_success.html', { 'book' : book, 'seller' : seller.username })
	else:
		return redirect('home')

def results(request):
	if request.user.is_authenticated():
		isbn = request.GET.get('isbn')
		books_queryset = BookListing.objects.filter(isbn_13=isbn).order_by("price").values()
		books = [entry for entry in books_queryset]
		return render(request, 'results.html', { 'books' : books })
	else:
		return redirect('home')

def search(request):
	if request.user.is_authenticated():
		if request.GET.get('isbn') is not None:
			isbn = request.GET.get('isbn')
			book = get_book_by_isbn(isbn)
			return render(request, 'search.html', { 'books' : [book] })
		elif request.GET.get('author') is not None:
			title = request.GET.get('title')
			author = request.GET.get('author')
			books = get_books_by_author_and_title(author, title)
			return render(request, 'search.html', { 'books' : books })
		else:
			return render(request, 'search.html', {})
	else:
		return redirect('home')

def listing_complete(request):
	if request.user.is_authenticated():
		if request.method == "POST":
			title = request.POST.get('title')
			author = request.POST.get('author')
			isbn = request.POST.get('isbn')
			edition = request.POST.get('edition')[0]
			condition = request.POST.get('condition')[0]
			price = Decimal(request.POST.get('price'))

			new_listing = BookListing(
			    isbn_13 = isbn,
			    price = price,
			    condition = condition,
			    cover_type = edition,
			    seller = request.user,
			    author = author,
			  	title = title
			    )
			new_listing.save()

			return redirect('home')
	else:
		return redirect('home')

# TODO: add redis condition get-ing inside here...
# also, update the HTML template to show this info!!
def finish_listing(request):
	if request.user.is_authenticated():
		if request.method == "POST":
				title = request.POST.get('title')
				author = request.POST.get('author')
				isbn = request.POST.get('isbn')
				edition = request.POST.get('edition')

				new = cache.get(isbn + '5')
				if (new == None):
					new = "not available"
				else:
					new = new['sales_total'] / new['number_sold']

				like_new = cache.get(isbn + '4')
				if (like_new == None):
					like_new = "not available"
				else:
					like_new = like_new['sales_total'] / like_new['number_sold']

				good = cache.get(isbn + '3')
				if (good == None):
					good = "not available"
				else:
					good = good['sales_total'] / good['number_sold']

				fair = cache.get(isbn + '2')
				if (fair == None):
					fair = "not available"
				else:
					fair = fair['sales_total'] / fair['number_sold']

				poor = cache.get(isbn + '1')
				if (poor == None):
					poor = "not available"
				else:
					poor = poor['sales_total'] / poor['number_sold']

				return render(request, 'finish_listing.html',{ 'book':
				              {
				              	'title' : title,
				              	'author' : author,
				              	'isbn' : isbn,
				              	'edition' : edition
				              }, 'price_suggest' : {
				              	'new' : new,
				              	'like_new' : like_new,
				              	'good' : good,
				              	'fair' : fair,
				              	'poor' : poor
				              }
				              })
		else:
			return redirect('home')
	else:
		return redirect('home')

def list_new(request):
	if request.user.is_authenticated():
		if request.method == "POST":
			if request.POST.get('isbn') is not None:
				isbn = request.POST.get('isbn')
				book = get_book_by_isbn(isbn)
				return render(request, 'choose_new.html', {'books': [book]})
			else:
				title = request.POST.get('title')
				author = request.POST.get('author')
				books = get_books_by_author_and_title(author, title)
				return render(request, 'choose_new.html', {'books': books})
		else:
			return render(request, 'list_new.html', {})
	else:
		return redirect('home')

# (this is when user marks their book as gone)
# TODO: get this isbn/condition's info from redis
#		get from BookListing how much the price was
#		update the redis sales total with this price
#			and increment number sold
# ^ do all this *bef0re* you delete the book
def sold(request):
	if request.user.is_authenticated():
		book_id = request.POST.get('bookId')
		book = BookListing.objects.get(id = book_id)#.select_related('seller')
		if book.seller.id == request.user.id:
			book_isbn = book.isbn_13
			book_condition = book.condition
			book_price = book.price
			#key values in cache for books will be isbn concatenated with condition
			#	for ease of programming
			book_key = book_isbn + book_condition
			value = cache.get(book_key)
			if value == None:
				cache.set(book_key,{'number_sold':1, 'sales_total': book_price})
			else:
				new_number_sold = value['number_sold'] + 1
				new_sales_total = value['sales_total'] + book_price
				cache.set(book_key, {'number_sold': new_number_sold, 'sales_total': new_sales_total})
			book.delete()
		return redirect('home')
	else:
		return redirect('home')

def home(request):
	if request.user.is_authenticated():
		books_queryset = BookListing.objects.filter(seller__id = request.user.id).order_by("-title").values()
		books = [entry for entry in books_queryset]
		return render(request, 'user.html', {'user' : request.user, 'books': books})
	else:
		return render(request, 'home.html', {})

def register(request):
	if request.method == "POST":
		username = request.POST.get('username')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email = request.POST.getlist('email')[0]
		location = request.POST.getlist('location')
		password = request.POST.get('password')
		loc, created = Location.objects.get_or_create(name=location)

		user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
		# user.profile.location=loc
		# user.save()

		profile = UserProfile(user=user, location=loc)

		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)

		return redirect('home')
	else:
		return render(request, 'register.html', {})

def log_in(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)

		return redirect('home')
	else:
		return render(request, 'login.html', {})

def log_out(request):
	if request.user.is_authenticated():
		logout(request)
	return redirect('home')


##########################################################################################

# def get_listing_for_isbn(request, isbn):
# 	isbn_listing_info_out = []

# 	if len(arg_dict) == 0:
# 		return HttpResponse("Invalid number of arguments")

# 	valid_filter_dict = get_valid_filter_dict(request.GET)

# 	if len(valid_filter_dict) == 0:
# 		return HttpResponse("Invalid arguments provided")

# 	if request.user.is_authenticated() and request.user.id:
# 		try:
# 			user_profile = UserProfile.objects.get(user_id=request.user.id) # ??
# 		except UserProfile.DoesNotExist:
# 			return HttpResponse("User profile does not exist")
# 		valid_dict['location'] = user_profile.location

# 	book_listings = BookListing.objects.filter(**valid_filter_dictarg_dict)

# 	for book_listing in book_listings:
# 		isbn_listing_info_out.append((book_listing.seller, book_listing.price, book_listing.condition))

# 	return render(request, 'book_exchange/listing', isbn_listing_info_out)

# def get_valid_filter_dict(input_dict):
# 	# Title (optional), Author (optional), ISBN (optional) (must specify at least one)
# 	valid_arg_list = ['title', 'author', 'isbn_13']
# 	valid_filter_dict = {}

# 	for valid_arg in valid_arg_list:
# 		if valid_arg in input_dict:
# 			valid_filter_dict[valid_arg] = input_dict[valid_arg]

# 	return valid_filter_dict

# ##########################################################################################

# def send_purchase_request_email(request):
# 	if request.user.is_authenticated() and request.user.id:

# 		try:
# 			inquirer_profile = UserProfile.objects.get(user_id=request.user.id)
# 		except UserProfile.DoesNotExist:
# 			return HttpResponse("Inquirer's user profile does not exist")

# 		try:
# 			seller_profile = request.GET.get("seller")
# 		except KeyError:
# 			return HttpResponse("Seller's user profile does not exist")

# 		try:
# 			isbn_13 = request.GET.get("isbn_13") # somehow map the ISBN to the title for the email?
# 		except KeyError:
# 			return HttpResponse("ISBN does not exist")

# 		try:
# 			book_title = BookListing.objects.get(isbn_13=isbn_13).title
# 		except BookListing.DoesNotExist:
# 			return HttpResponse("No book title matching ISBN exists")

# 		send_mail(
# 			"Book sale inquiry",
# 			"%s would like to buy your copy of %s. Please email them at %s." % (inquirer_profile.name, book_title, inquirer_profile.email,),
# 			inquirer_profile.email, # but this is an email field--can I do this?
# 			[seller_profile.email],
# 			auth_user=request.user
# 		)

# 	else:
# 		return HttpResponse("Not authenticated")

# ##########################################################################################

# """ TODO (requires calls to ISBN/BOOK API
# def list_a_book(request):
# 	if request.user.is_authenticated() and request.user.id:

# 		try:
# 			seller_profile = UserProfile.objects.get(user_id=request.user.id)
#     	except UserProfile.DoesNotExist:
# 			return HttpResponse("Seller's user profile does not exist")


# 		# TODO
# 		# issue a call to the books API to retrieve title, author, edition

# 		isbn_13   = request.GET.get('isbn_13')
# 		price     = request.GET.get('price')
# 		condition = request.GET.get('condition')
# 		title = ....
# 		author = ....
# 		edition = ....

# 		book_listing = models.BookListing(
# 			isbn_13=isbn_13,
# 			price=price,
# 			condition=condition,
# 			seller=seller_profile,
# 			title=title,
# 			author=author,
# 			edition=edition
# 		)

# 		# test whether a record for this isbn exists
# 		try:
# 			sales_total = IsbnSalesTotal.objects.get(isbn_13=isbn_13)
# 		except IsbnSalesTotal.DoesNotExist:
# 			sales_total = models.IsbnSalesTotal(
# 				isbn_13=isbn_13,
# 				copies_sold_NEW=0,
#     			copies_sold_LIKE_NEW=0,
#     			copies_sold_GOOD=0,
#     			copies_sold_FAIR=0,
#     			copies_sold_POOR=0,
#     			total_sales_amount_NEW=0.00,
#     			total_sales_amount_LIKE_NEW=000,
#     			total_sales_amount_GOOD=0.00,
#     			total_sales_amount_FAIR=0.00,
#     			total_sales_amount_POOR=0.00,
# 				total_copies_sold_ALL=0
# 			)
# 			sales_total.save()

# 		book_listing.save()

# 		return HttpResponse("Success")
# 	else:
# 		return HttpResponse("Not authenticated")
# """

# ##########################################################################################

# def see_own_book_listings(request):
# 	if request.user.is_authenticated() and request.user.id:
# 		try:
# 			seller_profile = UserProfile.objects.get(user_id=request.user.id)
# 		except UserProfile.DoesNotExist:
# 			return HttpResponse("Seller's user profile does not exist")

# 		try:
# 			own_book_listings = BookListing.objects.filter(seller=seller_profile)
# 		except BookListing.DoesNotExist:
# 			return HttpResponse("Book listings do not exist for this user")

# 		return render(request, 'book_exchange/personallistings', own_book_listings)
# 	else:
# 		return HttpResponse("Not authenticated")

# ##########################################################################################

# def delist_book(request):
# 	if request.user.is_authenticated() and request.user.id:
# 		try:
# 			seller_profile = UserProfile.objects.get(user_id=request.user.id)
# 		except UserProfile.DoesNotExist:
# 			return HttpResponse("Seller's user profile does not exist")

# 		try:
# 			book_to_delist = request.GET.get("BookListing")
# 		except KeyError:
# 			return HttpResponse("Book listing does not exist")

# 		try:
# 			is_sold = request.GET.get("is_sold")
# 		except KeyError:
# 			return HttpResponse("no such information available")

# 		if is_sold:
# 			# update sales total
# 			# if something fails here will we have to reverse all changes?
# 			try:
# 				sales_total = IsbnSalesTotal.objects.get(isbn_13=isbn_13)
# 			except IsbnSalesTotal.DoesNotExist:
# 				return HttpResponse("Sales total cannot be found, de-listing failed")

# 			isbn_13   = book_to_delist.isbn_13
# 			condition = book_to_delist.condition
# 			price     = book_to_delist.price

# 			# TODO : make this more generic (non-hard coded in case choices are changed)
# 			if condition == IsbnSalesTotal.NEW:
# 				sales_total.copies_sold_NEW += 1
# 				sales_total.total_sales_amount_NEW += price
# 			elif condition == IsbnSalesTotal.LIKE_NEW:
# 				sales_total.copies_sold_LIKE_NEW += 1
# 				sales_total.total_sales_amount_LIKE_NEW += price
# 			elif condition == IsbnSalesTotal.GOOD:
# 				sales_total.copies_sold_GOOD += 1
# 				sales_total.total_sales_amount_GOOD += price
# 			elif condition == IsbnSalesTotal.FAIR:
# 				sales_total.copies_sold_FAIR += 1
# 				sales_total.total_sales_amount_FAIR += price
# 			elif condition == IsbnSalesTotal.POOR:
# 				sales_total.copies_sold_POOR += 1
# 				sales_total.total_sales_amount_POOR += price
# 			else:
# 				return HttpResponse('Sales total error with "condition", de-listing failed')
# 			sales_total.total_copies_sold_ALL += 1

# 		# only delete if unsold or sold and updated successfully ?
# 		book_to_delist.delete()
# 	else:
# 		return HttpResponse("Not authenticated")

# ##########################################################################################

# """
# See Suggested Price
# Parameters: ISBN, Condition
# Output: a price.
# Side Effects: None
# Authentication: Not required.
# """
# """
# TODO: price suggestion
# def see_suggested_price(request):
# 	try:
# 		isbn_13 = request.GET.get("isbn_13")
# 	except KeyError:
# 		return HttpResponse("no such information available")
# 	try:
# 		condition = request.GET.get("condition")
# 	except KeyError:
# 		return HttpResponse("no such information available")

# 	# get suggested price using isbn_13 and condition

# """
# ##########################################################################################
# """
# Register an Account
# Parameters: Name, Location, Email
# Output: None
# Side Effects: Creates a user record
# Authentication: Not required (but needs email confirmation)
# """
# def register_account_information(request):
# 	if request.user.is_authenticated() and request.user.id:
# 		try:
# 			user_profile = UserProfile.objects.get(user_id=request.user.id)
# 		except UserProfile.DoesNotExist:
# 			location = models.Location(request.GET.get('location'))
# 			location.save()
# 			a_new_user = models.UserProfile(
# 					user_id=request.user.id,
# 					name=request.GET.get('name'),
# 					location=location,
# 					email= models.EmailField(unique=True) # comment line 2
# 			)
# 			a_new_user.save()
# 		else:
# 			return HttpResponse("user already exists")


# ##########################################################################################
# """
# Update Account Information
# Parameters: User, Name, Location, Email
# Output: None
# Side Effects: Updates a user record
# Authentication: Required
# """
# def update_account_information(request):
# 	if request.user.is_authenticated() and request.user.id:
# 		try:
# 			user_profile = UserProfile.objects.get(user_id=request.user.id)
# 		except UserProfile.DoesNotExist:
# 			return HttpResponse("no such user")

# 		something_to_change = False

# 		try:
# 			name = request.GET.get('name')
# 		except KeyError:
# 			pass
# 		else:
# 			something_to_change = True
# 			user_profile.name = name

# 			# do we change this? request.user.username = name # ?????

# 		try:
# 			location = request.GET.get('location')
# 		except KeyError:
# 			pass
# 		else:
# 			something_to_change = True
# 			user_profile.location = location


# 		try:
# 			email = request.GET.get('email')
# 		except KeyError:
# 			pass
# 		else:
# 			something_to_change = True
# 			user_profile.email = email

# 		if something_to_change:
# 			user_profile.save()
# 			return HttpResponse("user information changed")
# 		else:
# 			return HttpResponse("Nothing to change")
# 	else:
# 		return HttpResponse("Not authenticated")

# ##########################################################################################
