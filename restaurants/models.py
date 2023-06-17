from django.db import models
from django.contrib.postgres.fields import ArrayField


class Restaurants(models.Model):
    business_id = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    postal_code = models.IntegerField()
    stars = models.IntegerField()
    categories = ArrayField(models.CharField(max_length=20), default=list)
    text = models.CharField(max_length=300)
