from django.db import models


class Review(models.Model):
    SENTIMENT_CHOICES = (
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.FloatField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, null=True)

    def __str__(self):
        return self.title


#Create the proj in django,with reg,login,after login the user will inpit the url and click start,the system should start working,after that it should show the analytics in graphical and tabular format