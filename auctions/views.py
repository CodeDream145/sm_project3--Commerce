from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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
        wl = Watchlists(user = user)
        wl.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
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

def listing(request, title):
    listing = Listings.objects.get(title = title)
    if request.user.is_authenticated:
        watchlist = Watchlists.objects.get(user = request.user)
        watchlist = watchlist.listing.all()
    else:
        watchlist = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist
    })

@login_required(login_url='login')
def watchlists(request):
    
    watchlists = Watchlists.objects.get(user = request.user)
    return render(request, "auctions/watchlists.html", {
        "watchlists": watchlists.listing.filter(status = True).all()
    })

@login_required(login_url='login')
def add_watchlist(request, title):
    watchlists = Watchlists.objects.get(user = request.user)
    listing = Listings.objects.get(title = title)
    watchlists.listing.add(listing)

    return HttpResponseRedirect(reverse("watchlists"))


@login_required(login_url='login')
def remove_watchlist(request, title):
    watchlists = Watchlists.objects.get(user = request.user)
    listing = Listings.objects.get(title = title)
    watchlists.listing.remove(listing)

    return HttpResponseRedirect(reverse("watchlists"))

@login_required(login_url='login')
def bid(request, title):
    try:
        listing = Listings.objects.get(title = title)
    except ObjectDoesNotExist:
        return HttpResponse("<h1 style='text-align: center;'>404 Requested Page Not Found.<h1>")

    if request.user.is_authenticated:
        watchlist = Watchlists.objects.get(user = request.user)
        watchlist = watchlist.listing.all()
    else:
        watchlist = None

    bid_error = []
    bid = request.POST["user_bid"]
    try:
        bid = float(bid)
    except ValueError:
        bid_error = "Invalid Bid!"
    
    if not bid_error:
        hb = listing.highest_bid()
        if bid <= listing.min_bid:
            bid_error = "Bid Must Be Atleast Higher Than The Minimum Bid."
        elif hb and bid <= hb.bid_amount :
            bid_error = "Bid Must Be Higher Than The Current Highest Bid."
    
    if bid_error:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watchlist": watchlist,
            "bid_error": bid_error
        })
    
    bidding = Biddings(user = request.user, listing = listing, bid_amount = bid)
    bidding.save()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "g_message": "Bidded Successfully"
    })

@login_required(login_url='login')
def close_auction(request, title):

    try:
        listing = Listings.objects.get(title = title)
    except ObjectDoesNotExist:
        return HttpResponse("<h1 style='text-align: center;'>404 Requested Page Not Found.<h1>")

    if not listing.listed_user == request.user:
        return HttpResponse("<h1 style='text-align: center;'>403 Permission Denied!<h1>")
    
    hb = listing.highest_bid()

    if not hb:
        listing.status = False
        listing.save()
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "r_message": f'Auction Closed and Product "UNSOLD".'
        })

    listing.winner = hb.user    
    listing.status = False
    listing.save()
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "g_message": f'Auction Closed and "{hb.user}" won the Auction for ${hb.bid_amount}'
    })

@login_required(login_url='login')
def comments(request, title):
    try:
        listing = Listings.objects.get(title = title)
    except ObjectDoesNotExist:
        return HttpResponse("<h1 style='text-align: center;'>404 Requested Page Not Found.<h1>")

    comment = (request.POST["user_comment"])

    if not comment or not len(str(comment)) <=2000:
        if request.user.is_authenticated:
            watchlist = Watchlists.objects.get(user = request.user)
            watchlist = watchlist.listing.all()
        else:
            watchlist = None

        if not comment:
            comment_error = "No Comment provided"
        elif not len(str(comment)) <=2000:
            comment_error = "Comment can only be upto 2000 characters."
        
        if comment_error:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "watchlist": watchlist,
                "comment_error": comment_error,
                "comment" : str(comment)
            })
    user_comment = Comments(user = request.user, listing = listing, comment = str(comment))
    user_comment.save()
    return HttpResponseRedirect(reverse('listing', args=(listing.title,)))

def categories(request):
    return render(request, "auctions/all_categories.html", {
        "categories": Categories.objects.all(),
    })

def s_category(request, category):
    try:
        category = Categories.objects.get(category=category)
    except ObjectDoesNotExist:
        return HttpResponse("<h1 style='text-align: center;'>404 Requested Page Not Found.<h1>")
    
    listings = Listings.objects.filter(category=category)

    return render(request, "auctions/s_category.html", {
        "listings": listings,
        "category": category.category,
    })