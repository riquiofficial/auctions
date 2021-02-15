from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/<str:closed>", views.index, name="index_closed"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("auction/<int:auction_id>/<str:active>",
         views.auction, name="auction_close"),
    path("create-new-listing", views.new_listing, name="new"),
    path("success/<str:name>", views.success, name="success"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<str:auction>", views.watchlist, name="watchlist_add"),
    path("watchlist/<str:auction>/<str:delete>",
         views.watchlist, name="watchlist_delete"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="categories"),
    path("bids", views.my_bids, name="my_bids"),
    path("auctions", views.my_auctions, name="my_auctions")
]
