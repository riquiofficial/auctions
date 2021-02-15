from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Auction", blank=True, default=None)


class Auction(models.Model):
    FASHION = 'FA'
    TOYS = 'TO'
    ELECTRONICS = 'EL'
    HOME = 'HO'
    BOOKS = 'BO'
    ENTERTAINMENT = 'EN'
    HEALTH = 'HE'
    INDUSTRY = 'IN'
    AUTOMOTIVE = 'AU'
    FOOD = 'FO'
    OTHER = 'OT'

    categories = [
        (FASHION, "Fashion, Clothing and Accessories"),
        (TOYS, "Children's Toys"),
        (ELECTRONICS, "Electronics"),
        (HOME, 'Home and Garden'),
        (BOOKS, 'Books'),
        (ENTERTAINMENT, 'Films, TV and Games'),
        (HEALTH, 'Health'),
        (INDUSTRY, 'Industry'),
        (AUTOMOTIVE, 'Automotive'),
        (FOOD, 'Food and Drink'),
        (OTHER, 'Other')
    ]

    item_name = models.CharField(max_length=200)
    description = models.TextField(max_length=800)
    start_price = models.DecimalField(max_digits=20, decimal_places=2)
    seller = models.ForeignKey(
        "User", default=None, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(
        default=(timezone.now()+timezone.timedelta(days=7)))
    photo = models.URLField(
        max_length=400, null=True, blank=True)
    category = models.CharField(
        max_length=2, choices=categories, default=OTHER)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Auction {self.id}: {self.item_name}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    auction = models.ForeignKey(
        Auction, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} has bid {self.bid_price} on item ({self.auction.id}) {self.auction.item_name}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    auction = models.ForeignKey(
        Auction, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment on auction {self.auction.id}: {self.auction.item_name} by {self.author}: '{self.comment[0:30]}..."
