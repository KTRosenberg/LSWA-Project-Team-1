# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-06 16:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BookListing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn_13', models.CharField(db_index=True, max_length=13)),
                ('price', models.DecimalField(decimal_places=2, max_digits=4)),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('author', models.CharField(db_index=True, max_length=101)),
                ('edition', models.CharField(blank=True, max_length=16)),
                ('cover_type', models.CharField(choices=[('H', 'hardcover'), ('S', 'paperback'), ('U', 'unknown')], default='U', max_length=1)),
                ('condition', models.CharField(choices=[('5', 'new'), ('4', 'like new'), ('3', 'good'), ('2', 'fair'), ('1', 'poor')], max_length=1)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IsbnSalesTotal',
            fields=[
                ('isbn_13', models.CharField(db_index=True, max_length=13, primary_key=True, serialize=False)),
                ('copies_sold_NEW', models.PositiveIntegerField()),
                ('copies_sold_LIKE_NEW', models.PositiveIntegerField()),
                ('copies_sold_GOOD', models.PositiveIntegerField()),
                ('copies_sold_FAIR', models.PositiveIntegerField()),
                ('copies_sold_POOR', models.PositiveIntegerField()),
                ('total_sales_amount_NEW', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_sales_amount_LIKE_NEW', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_sales_amount_GOOD', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_sales_amount_FAIR', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_sales_amount_POOR', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total_copies_sold_ALL', models.PositiveIntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bookexchange.Location')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
