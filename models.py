from django.db import models

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    sentiment = models.CharField(max_length=20)
    url = models.URLField(max_length=255, default='https://amazon.in')

    def __str__(self):
        return self.title
