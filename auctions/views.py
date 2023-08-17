from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    
    if request.method == "POST":
        user = request.user
        title = str(request.POST["title"])
        description = str(request.POST["description"])
        img_url = str(request.POST["img_url"])
        category = str(request.POST["category"])
        min_bid = request.POST["min_bid"]

        error_messages ={}

        if not min_bid:
            error_messages["minbid_error"] = "Must Provide the Minimum Amount for the Bidders"

        try:
            min_bid = float(min_bid)
        except ValueError:
            error_messages["minbid_error"] = "Invalid Value"


        if not title:
            error_messages["title_error"] = "Must Provide Title"
        if not description:
            error_messages["description_error"] = "Must Provide Description" 
        if not min_bid:
            error_messages["minbid_error"] = "Must Provide the Minimum Amount for the Bidders"
        if not category:
            error_messages["category_error"] = "Must Select Category"

        try:
            category = Categories.objects.get(category = category)
        except ObjectDoesNotExist:
            error_messages["category_error"] = "Invalid Category"

        if error_messages:
            return render(request, "auctions/add_listing.html", {
                "title":title,
                "description": description,
                "img_url": img_url,
                "min_bid": min_bid,
                "e_category": category,
                "categories": Categories.objects.all(),
                **error_messages
            })

        listing = Listings(listed_user = user, title = title, description = description, min_bid = min_bid, img_url = img_url, category = category)
        listing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/add_listing.html", {
        "categories": Categories.objects.all()
    })