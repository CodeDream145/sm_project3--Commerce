from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<str:title>", views.listing, name="listing"),
    path("watchlists", views.watchlists, name="watchlists"),
    path("add_watchlist/<str:title>",views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<str:title>", views.remove_watchlist, name="remove_watchlist"),
    path("bid/<str:title>", views.bid, name="bid"),
    path("close_auction/<str:title>", views.close_auction, name="close_auction"),
    
]
