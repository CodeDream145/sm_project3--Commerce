from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Listings)
admin.site.register(Watchlists)
admin.site.register(Biddings)
admin.site.register(Comments)