# Generated by Django 4.2.2 on 2023-08-18 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_listings_winner_alter_listings_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listings',
            old_name='Winner',
            new_name='winner',
        ),
    ]
