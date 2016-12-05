import requests
import json

books_api_key = json.loads(open('../appserver/config.json').read())["google_books_key"]
isbn_api_key = json.loads(open('../appserver/config.json').read())["isbndb_key"]

books_api_url = "https://www.googleapis.com/books/v1/volumes"
isbn_api_url = "http://isbndb.com/api/v2/json/%s/book" % (isbn_api_key)

# if also want published_date, make fields param = 'items(volumeInfo(authors,industryIdentifiers,publishedDate,title))'

# TO DO notes:
#	validation / checking:
#		does it have an ISBN identifier?
#		is it really a book (?) [see 'categories', 'printType', etc]
# 	use google *only* for getting the ISBNs - get all other data from isbndb (?)
#		or, get all data from google, and only go to isbndb for editions
#		^ either way, always get the data (excl. edition_info) from the same source

def get_book_by_isbn(isbn):
	isbn_query_string = 'isbn:%s' % isbn
	params = { 'key' : books_api_key,
				'q' : isbn_query_string,
				'fields' : 'items(volumeInfo(authors,industryIdentifiers,title))'
			 }
	book_response = requests.get(books_api_url, params=params)
	book_data = book_response.json()
	return book_data['items'][0]

	# api_url = "http://isbndb.com/api/v2/json/VHFOB4SZ/book/%s" % (isbn)
	# book_response = requests.get(api_url)
	# book_data = book_response.json()
	# return book_data

def get_books_by_author(author):
	author_query_string = 'inauthor:"%s"' % author
	params = { 'key' : books_api_key,
				'q' : author_query_string,
				'fields' : 'items(volumeInfo(authors,industryIdentifiers,title))'
			 }
	book_response = requests.get(books_api_url, params=params)
	book_data = book_response.json()
	if 'items' in book_data:
		return book_data['items']
	else:
		return {}

	# api_url = "http://isbndb.com/api/v2/json/VHFOB4SZ/books"
	# params = {'q': author, 'i': 'author_name'}
	# books_response = requests.get(api_url, params = params)
	# book_data = books_response.json()
	# return book_data

def get_books_by_title(title):
	title_query_string = 'intitle:"%s"' % title
	params = { 'key' : books_api_key,
				'q' : title_query_string,
				'fields' : 'items(volumeInfo(authors,industryIdentifiers,title))'
			 }
	book_response = requests.get(books_api_url, params=params)
	book_data = book_response.json()
	if 'items' in book_data:
		return book_data['items']
	else:
		return {}

	# api_url = "http://isbndb.com/api/v2/json/VHFOB4SZ/books"
	# params = {'q': title}
	# books_response = requests.get(api_url, params = params)
	# book_data = books_response.json()
	# return book_data

def get_books_by_author_and_title(author, title):
	if not author or author.isspace():
		return get_books_by_title(title)
	elif not title or title.isspace():
		return get_books_by_author(author)
	else:
		author_query_string = 'inauthor:"%s"' % author
		title_query_string = 'intitle:"%s"' % title
		query_string = '%s %s' % (author_query_string, title_query_string)
		params = { 'key' : books_api_key,
					'q' : query_string,
					'fields' : 'items(volumeInfo(authors,industryIdentifiers,title))',
					'maxResults' : '10'
				 }
		book_response = requests.get(books_api_url, params=params)
		book_data = book_response.json()
		for book in book_data['items']:
		    print(book)
		print()
		print(book_response.text)
		print()

		if 'items' in book_data:
			print(len(book_data['items']))
			add_editions_to_books(book_data['items'])
			return book_data['items']
		else:
			return {}

def add_editions_to_books(books):
	index = 0
	for book in books:
		if "industryIdentifiers" not in book['volumeInfo']:
			print(book)
			del books[index]
		else:
			try:
				set_edition_info_for_book(book)
			except NoIsbnException:
				print("no isbn")
				print(book)
				del books[index]
		index += 1
	return

def get_isbn_for_book_json(book):
	identifiers = book['volumeInfo']['industryIdentifiers']
	for identifier in identifiers:
		if "ISBN" in identifier['type']:
			return identifier['identifier']
	raise NoIsbnException("no isbn identifier present")

def set_edition_info_for_book(book):
	isbn = get_isbn_for_book_json(book)
	edition_info = get_edition_info_for_isbn(isbn)
	if "error" not in edition_info:
		book['volumeInfo']['edition_info'] = edition_info['data'][0]['edition_info']
	else:
		book['volumeInfo']['edition_info'] = 'unknown'
	return

def get_edition_info_for_isbn(isbn):
	api_url = "%s/%s" % (isbn_api_url, isbn)
	book_response = requests.get(api_url)
	book_data = book_response.json()
	return book_data

class NoIsbnException(Exception):
    pass


print("author and title")
for book in get_books_by_author_and_title("David Lay", "Linear Algebra"):
	print(book)
	print()
print()
print()
print("title")
for book in get_books_by_author_and_title("", "Linear Algebra"):
	print(book)
	print()
print()
print()
print("author")
for book in get_books_by_author_and_title("David Lay", ""):
	print(book)
	print()
print()
print()