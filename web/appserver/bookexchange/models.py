# data model drafting
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
import django.core.validators

from django.dispatch import receiver
from django.db.models.signals import post_save


# Karl Toby Rosenberg, data model drafts ver 2, took Kate's suggestions

"""
Models

UserProfile
Book for sale
City
Sales total (per ISBN-13)
"""

class Location(models.Model):
    """
    A location (e.g. city, town)
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

class UserProfile(models.Model):
    """
    A UserProfile
    ...has one name
    ...has one city (foreign key)
    ...has one email address
    """
    # user_id  = models.BigIntegerField(primary_key=True)
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    # name     = models.CharField(max_length=64)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    # email    = models.EmailField(unique=True)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class BookListing(models.Model):
    """
    A book for sale
    ...has one ISBN-13
    ...has one price
    ...has one condition
    ...is owned by one UserProfile, the seller (foreign key)
    ...has one title (secondary index)
    ...has one author (secondary index)
    ...has one edition
    ...is one of either hardcover, softcover, or unknown
    """
    isbn_13   = models.CharField(max_length=13, db_index=True) # comment line 4: like this?
    price     = models.DecimalField(decimal_places=2, max_digits=4) # comment line 5
    # condition = models.CharField(max_length=32)
    seller    = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length=256, db_index=True)
    author    = models.CharField(max_length=101, db_index=True) # comment line 6
    edition   = models.CharField(max_length=16, blank=True)

    # COVER TYPE
    # hardcover, softcover, or unknown
    HARDCOVER = 'H'
    PAPERBACK = 'S'
    UNKNOWN   = 'U'
    COVER_TYPE_CHOICES = (
        (HARDCOVER, 'hardcover'),
        (PAPERBACK, 'paperback'),
        (UNKNOWN,   'unknown')
    )
    cover_type = models.CharField(max_length=1, choices=COVER_TYPE_CHOICES, default=UNKNOWN)

    # CONDITION TYPE
    NEW      = '5'
    LIKE_NEW = '4'
    GOOD     = '3'
    FAIR     = '2'
    POOR     = '1'
    CONDITION_TYPE_CHOICES = (
        (NEW,'new'),
        (LIKE_NEW, 'like new'),
        (GOOD, 'good'),
        (FAIR, 'fair'),
        (POOR, 'poor')
    )
    condition = models.CharField(max_length=1, choices=CONDITION_TYPE_CHOICES, blank=False)

# removed b/c not actually in DB - in redis
# class IsbnSalesTotal(models.Model):
#     """
#     A sales total
#     ...has one publication (i.e., ISBN-13) as its primary key

#     ...has many conditions, and for each one:
#     ...has one dollar amount
#     ...has one number of copies sold
#     """
#     isbn_13   = models.CharField(max_length=13, primary_key=True, db_index=True)

#     copies_sold_NEW      = models.PositiveIntegerField()
#     copies_sold_LIKE_NEW = models.PositiveIntegerField()
#     copies_sold_GOOD     = models.PositiveIntegerField()
#     copies_sold_FAIR     = models.PositiveIntegerField()
#     copies_sold_POOR     = models.PositiveIntegerField()

#     total_sales_amount_NEW       = models.DecimalField(decimal_places=2, max_digits=4)
#     total_sales_amount_LIKE_NEW  = models.DecimalField(decimal_places=2, max_digits=4)
#     total_sales_amount_GOOD      = models.DecimalField(decimal_places=2, max_digits=4)
#     total_sales_amount_FAIR      = models.DecimalField(decimal_places=2, max_digits=4)
#     total_sales_amount_POOR      = models.DecimalField(decimal_places=2, max_digits=4)

#     # would this allow us to display the best sellers in exchange for another field?
#     total_copies_sold_ALL = models.PositiveIntegerField(db_index=True)