# data model drafting
from django.db import models
from django import forms
from django.core.exceptions import ValidationError
import django.core.validators 
from django.utils.translation import ugettext_lazy as # do I need this?


# Karl Toby Rosenberg, data model drafts ver 2, took Kate's suggestions

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
    location = models.ForeignKey(Location, on_delete=models.PROTECT) # comment line 1
    email    = models.EmailField(unique=True) # comment line 2

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
    isbn_13   = models.CharField(max_length=13, db_index=True, max_length=13, validators=[MinLengthValidator(13)]) # comment line 4: like this?
    price     = models.DecimalField(decimal_places=2) # comment line 5
    condition = models.CharField(max_length=32) 
    seller    = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length=256, db_index=True)
    author    = models.CharField(max_length=101, db_index=True) # comment line 6
    edition   = models.CharField(max_length=16)
    
    # COVER TYPE
    # hardcover, softcover, or unknown
    HARDCOVER = 'H'
    SOFTCOVER = 'S'
    UNKNOWN   = None # not sure if it accepts None as an option
    COVER_TYPE_CHOICES = (
        (HARDCOVER, 'hardcover'),
        (SOFTCOVER, 'softcover'),
        (UNKNOWN,   'unknown')
    )
    cover_type = models.CharField(max_length=9, choices=COVER_TYPE_CHOICES, default=UNKNOWN)
    
    
    # CONDITION TYPE
    NEW      = '5'
    LIKE_NEW = '4'
    GOOD     = '3
    FAIR     = '2'
    POOR     = '1'
        
    CONDITION_TYPE_CHOICES = (
        (NEW,'5'),
        (LIKE_NEW, '4'),
        (GOOD, '3'),
        (FAIR, '2'),
        (POOR, '1')
    )
    condition = models.CharField(max_length=1, choices=CONDITION_TYPE_CHOICES, blank=False)

class Location(models.model):
    """   
    A city ( I named this Location since maybe the user doesn't necessarily live in a city )
    ...has one name
    """
    name = models.CharField(max_length=64, db_index=True)
    # comment line 23: I am not sure. We could concatenate that information maybe...
    # otherwise:
    """
    city = models.CharField(max_length=64, db_index=True)
    state = models.CharField(max_length=64, db_index=True)
    # optional
    institution = models.CharField(max_length=64, db_index=True, blank=True)
    """

class IsbnSalesTotal(models.model):
    """
    A sales total
    ...has one publication (i.e., ISBN-13) as its primary key
    
    ...has many conditions, and for each one:
    ...has one dollar amount
    ...has one number of copies sold
    """
    isbn_13   = models.CharField(max_length=13, primary_key=True, db_index=True, max_length=13, validators=[MinLengthValidator(13)])
    
    copies_sold_NEW      = models.PositiveIntegerField()
    copies_sold_LIKE_NEW = models.PositiveIntegerField()
    copies_sold_GOOD     = models.PositiveIntegerField()
    copies_sold_FAIR     = models.PositiveIntegerField()
    copies_sold_POOR     = models.PositiveIntegerField()

    total_sales_amount_NEW       = models.DecimalField(decimal_places=2)
    total_sales_amount_LIKE_NEW  = models.DecimalField(decimal_places=2)
    total_sales_amount_GOOD      = models.DecimalField(decimal_places=2)
    total_sales_amount_FAIR      = models.DecimalField(decimal_places=2)
    total_sales_amount_POOR      = models.DecimalField(decimal_places=2)
    
    # would this allow us to display the best sellers in exchange for another field?
    total_sales_amount_ALL = models.DecimalField(decimal_places=2, db_index=True) 
    