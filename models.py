# models.py

from django.db import models


class Review(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.FloatField()

    def __str__(self):
        return self.title
