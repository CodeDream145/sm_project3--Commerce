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