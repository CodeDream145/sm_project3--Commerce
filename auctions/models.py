from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


#categories
class Categories(models.Model):
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.category

#listings
class Listings(models.Model):
    listed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    status = models.BooleanField(default=True)    
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=4000)
    min_bid = models.DecimalField(decimal_places=2, max_digits=10)
    img_url = models.URLField(blank=True)
    category = models.ForeignKey(Categories, null=True, on_delete=models.SET_NULL, related_name="lists")
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="won")

    def __str__(self):
        return f'"{self.title}" by "{self.listed_user}" at the minimum bid of "${self.min_bid}".'
    
    def highest_bid(self):
        hb = self.bids.order_by('-bid_amount').first()
        return hb
#watchlist
class Watchlists(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists", unique=True)
    listing = models.ManyToManyField(Listings,related_name="watching_users", blank=True)

    def __str__(self):
        return self.user
    
#bidding
class Biddings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(decimal_places=2, max_digits=10)

#comments
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_comments")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=2000)

    def __str__(self):
        return f'[{self.user}] on [{self.listing}]'  