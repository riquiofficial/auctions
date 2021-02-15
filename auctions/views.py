# authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# errors
from django.db import IntegrityError

# urls
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

# utils
from django.forms import ModelForm
from django.contrib import messages
from django.utils import timezone
from .util import match_max_bid_with_auction, get_max_bid

# models
from .models import User, Auction, Bid, Comment


class NewAuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['item_name', 'description',
                  'start_price', 'category', 'photo', 'end_date']

    # adding "form-control" class to each input field for style
    def __init__(self, *args, **kwargs):
        super(NewAuctionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_price']


class NewCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


def index(request, closed=False, selling=False):
    auctions = Auction.objects.filter(active=True)
    active = "Active"
    # closed auctions page
    if closed == "closed":
        auctions = Auction.objects.filter(active=False)
        active = "Closed"

    # return dictionary of max bid prices for each auction using its auction id as the key
    # key will be used to match the id for each auction id in the index template
    prices = match_max_bid_with_auction(auctions)
    return render(request, "auctions/index.html", {"auctions": auctions, "prices": prices, "active": active})


@ login_required(login_url='login')
def my_bids(request):
    all_user_bids = Bid.objects.filter(user=request.user)

    return render(request, "auctions/bids.html", {"user_bids": all_user_bids})


def auction(request, auction_id, active=True):
    auction = Auction.objects.get(pk=auction_id)
    comments = Comment.objects.filter(auction__id__exact=auction_id)
    bids = Bid.objects.filter(auction__id__exact=auction_id)
    form = NewBidForm()
    new_comment_form = NewCommentForm()
    max_bid = get_max_bid(bids)

    # close auction
    # double check active user is seller

    if request.user == auction.seller:
        if active != True:
            auction.active = False
            auction.save()

    watchlist = ""
    # discover whether auction is on user's watchlist
    if request.user.is_authenticated:
        try:
            watchlist = request.user.watchlist.get(pk=auction_id)
        except Auction.DoesNotExist:
            watchlist = ""

    # submit bids or comments
    if request.method == "POST":
        # bid:
        if "bid_price" in request.POST:
            form = NewBidForm(request.POST)

            if form.is_valid():
                bid_price = form.cleaned_data["bid_price"]

                # make sure the bid is over the current highest bid price
                if bid_price > max_bid["highest_bid"] and bid_price > auction.start_price:
                    new_bid = Bid.objects.create(user=request.user, bid_price=bid_price,
                                                 auction=auction)
                    new_bid.save()
                    messages.success(
                        request, f"Bid of £{bid_price} successful")
                    return HttpResponseRedirect(f'{auction_id}')
                else:
                    messages.error(
                        request, "Please enter a bid higher than the highest bid price or starting price.")

            else:
                messages.error(
                    request, "Please enter a bid higher than the highest bid price or starting price.")
        else:
            # comments
            sent_comment_form = NewCommentForm(request.POST)

            if sent_comment_form.is_valid():
                new_comment_message = sent_comment_form.cleaned_data["comment"]
                new_comment = Comment.objects.create(
                    author=request.user, auction=auction, comment=new_comment_message)
                new_comment.save()
                messages.success(request, "Your comment has been added")
            else:
                print(sent_comment_form)
                messages.error(request, "something went wrong")

    return render(request, "auctions/auction.html", {"auction": auction, "comments": comments, "max_bid": max_bid,  "form": form, "comment_form": new_comment_form, "watchlist": watchlist})


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


@ login_required(login_url='login')
def new_listing(request):
    if request.method == "POST":
        form = NewAuctionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["item_name"]
            new_auction = form.save(commit=False)
            new_auction.seller = request.user
            new_auction.start_date = timezone.now()
            new_auction.save()

            return redirect('success', name=name)

        else:
            return messages.error(request, "please try again")
    return render(request, 'auctions/newlisting.html', {'form': NewAuctionForm()})


def success(request, name):
    return render(request, 'auctions/success.html', {"list_name": name})


@ login_required(login_url='login')
def watchlist(request, auction="", delete=False):
    watchlist_items = request.user.watchlist.all()
    prices = match_max_bid_with_auction(watchlist_items)

    # add new auction to watchlist button
    if auction:
        user = request.user
        add_to_watchlist = Auction.objects.get(pk=auction)
        if delete:
            user.watchlist.remove(add_to_watchlist)
            delete = False
            messages.warning(request, "Item removed from Watchlist!")
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            user.watchlist.add(add_to_watchlist)
            messages.success(request, "Item added to Watchlist!")
            return HttpResponseRedirect(reverse("index"))

    return render(request, 'auctions/watchlist.html', {"watchlist": watchlist_items, "prices": prices})


def categories(request, category=False):
    if category:
        list_by_category = Auction.objects.filter(
            category=category)
    else:
        list_by_category = False
    prices = match_max_bid_with_auction(list_by_category)

    return render(request, 'auctions/categories.html', {"category": list_by_category, "prices": prices})


def my_auctions(request):
    user_auctions = Auction.objects.filter(seller__exact=request.user)

    return render(request, "auctions/myauctions.html", {"user_auctions": user_auctions})
