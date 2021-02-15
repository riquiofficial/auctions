from decimal import Decimal, ROUND_DOWN
from django.db.models import Max
from .models import Bid

# gets maximum bid by taking a queryset as an argument, ensures it is to 2 dp


def get_max_bid(bids):
    # aggregate returns a dict with key of bid_price__max
    max_bid = bids.aggregate(Max('bid_price'))['bid_price__max']
    if max_bid:
        # ensure type is decimal with 2 dp
        max_bid = Decimal(bids.aggregate(Max('bid_price'))['bid_price__max']).quantize(
            Decimal('.01'), rounding=ROUND_DOWN)
        max_bidder = Bid.objects.filter(bid_price__exact=max_bid)[
            0].user.username
    else:
        max_bid = 0
        max_bidder = ""

    return {"username": max_bidder, "highest_bid": max_bid}

# match bids corresponding to auction by matching the bid with the auction ID.
# return the maximum of all bids for that auction
# and the username who bidded that amount on that auction in a dictionary


def match_max_bid_with_auction(queryset):
    prices = {}
    if queryset:
        for item in queryset:
            bids = Bid.objects.filter(auction__id__exact=item.id)
            if bids:

                # call get_max_bid from utilities for the highest bid on that item
                max_bid = get_max_bid(bids)["highest_bid"]
                prices[item.id] = max_bid
            else:
                # if no bid exists just use start price of auction
                prices[item.id] = item.start_price
        return prices

    else:
        return None
