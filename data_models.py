# data model drafting
from django.db import models

# Karl Toby Rosenberg, just drafting some of the data models, please read comments

"""
Models

User
Book for sale
City
Sales total (per ISBN-13)
"""

class User(models.model):
    """
    A user
    ...has one name
    ...has one city (foreign key)
    ...has one email address
    """
    name     = models.CharField(max_length=64)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL) # ??? not sure about the on_delete parameter meaning... hmmm
    email    = models.CharField(max_length=254) # apparently the standardized maximum length of a full email including punctuation is 254
    

class BookListing(models.model):
    """
    A book for sale
    ...has one ISBN-13
    ...has one price
    ...has one condition
    ...is owned by one user, the seller (foreign key)
    ...has one title (secondary index)
    ...has one author (secondary index)
    ...has one edition
    ...is one of either hardcover, softcover, or unknown
    """
    #ISBN could be a 13-char CharField or an int
    isbn_13   = models.CharField(max_length=13) #should db_index be True? How would we enforce a length of 13? In a method or in some "view?", also I assume we'd like to be able to index by this value
    price     = models.DecimalField()
    condition = models.CharField(max_length=32) # should we standardize this? as its own model? set values? how?
    seller    = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length=256, db_index=True)
    author    = models.CharField(max_length=64, db_index=True)
    # char? depends on format 
    edition   = models.CharField(max_length=16)
    # hardcover, softcover, or unknown--- use a NullBooleanField or use a Field.choices form?
    # maybe same for condition?
    
    """
        HARDCOVER = 'HC'
        SOFTCOVER = 'SC'
        UNKNOWN   = None # not sure if it accepts None as an option
        COVER_TYPE_CHOICES = (
            (HARDCOVER, 'hardcover'),
            (SOFTCOVER, 'softcover'),
            (UNKNOWN,   'unknown')
        )
        cover_type = models.CharField(max_length=2, choices=COVER_TYPE_CHOICES, default=UNKNOWN)
        
        # or
        
        http://stackoverflow.com/questions/7279239/django-how-to-change-values-for-nullbooleanfield-in-a-modelform
        
        # or ?
        
        cover_type = models.NullBooleanField(default="None")
        
        
        # condition options? or are we letting the user input paragraphs (or limited-size/number of sentences) 
        # of unique information?
        
        EXCELLENT = '5'
        GREAT     = '4'
        GOOD      = '3'
        FAIR      = '2'
        POOR      = '1'
        UNKNOWN   = '0'
        
        CONDITION_TYPE_CHOICES = (
            (EXCELLENT,'5'),
            (GREAT, '4'),
            (GOOD, '3'),
            (FAIR, '2'),
            (POOR, '1'),
            (UNKNOWN, '0') # just for a default maybe, but the user shouldn't be allowed to omit this information
        )
        condition = models.CharField(max_length=32, choices=CONDITION_TYPE_CHOICES, default=UNKNOWN)
    """
  

class Location(models.model):
    """   
    A city ( I named this Location since maybe the user doesn't necessarily live in a city )
    ...has one name
    """
    name = models.CharField(max_length=64, db_index=True)

class IsbnSalesTotal(models.model):
    """
    A sales total
    ...has one publication (i.e., ISBN-13) as its primary key
    
    ...has many conditions, and for each one: <-- What does this mean? Is condition a data model now?
                                                  how do I represent this, the dollar amount, and number of copies
    ...has one dollar amount
    ...has one number of copies sold
    """
    isbn_13 = models.CharField(max_length=13, primary_key=True)
    
    # ??? for each condition, how would this be done?
    copies_sold        = models.BigIntegerField()
    total_sales_amount = models.DecimalField()

# THOUGHTS ON BELOW?
"""    
BigAutoField¶

class BigAutoField(**options)[source]¶

New in Django 1.10.

A 64-bit integer, much like an AutoField except that it is guaranteed to fit numbers from 1 to 9223372036854775807.
^- but does it allow for 0, if not, BigIntegerField will have to do, but it would be a waste since we don't need negative numbers

BigIntegerField¶

class BigIntegerField(**options)[source]¶

A 64-bit integer, much like an IntegerField except that it is guaranteed to fit numbers from -9223372036854775808 to 9223372036854775807. The default form widget for this field is a TextInput.
"""
    