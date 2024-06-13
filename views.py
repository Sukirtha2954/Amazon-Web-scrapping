import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.shortcuts import render
from textblob import TextBlob
from .models import Review


from django.db.models import Count
import matplotlib.pyplot as plt



def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "user1" and password == "adminrights":
            return redirect('scrape_reviews')
        else:
            return HttpResponse("Invalid login")
    return render(request, 'reviews/login.html')


def scrape_reviews_view(request):
    if request.method == "GET":
        base_url = 'https://www.amazon.in/Samsung-Galaxy-Smartphone-Titanium-Storage/product-reviews/B0CQYGF1QY/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=1'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        page_number = 1
        total_reviews = 0
        while total_reviews < 193:
            url = base_url.format(page_number, page_number)
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            reviews = soup.find_all('div', {'data-hook': 'review'})

            print(f"Number of reviews found on page {page_number}: {len(reviews)}")  # Deb

            if not reviews:

                break

            for review in reviews:
                try:
                    title = review.find('a', {'data-hook': 'review-title'}).text.strip()
                    content = review.find('span', {'data-hook': 'review-body'}).text.strip()
                    rating = float(review.find('i', {'data-hook': 'review-star-rating'}).text.split()[0].replace(',', '.'))

                    # Sentiment Analysis
                    analysis = TextBlob(content)
                    sentiment = analysis.sentiment.polarity
                    if sentiment > 0:
                        sentiment_label = 'Positive'
                    elif sentiment < 0:
                        sentiment_label = 'Negative'
                    else:
                        sentiment_label = 'Neutral'

                    print(f"Title: {title}, Content: {content}, Rating: {rating}, Sentiment: {sentiment_label}")

                    Review.objects.create(
                        title=title,
                        content=content,
                        rating=rating,
                        sentiment=sentiment_label
                    )
                    total_reviews += 1
                except Exception as e:
                    print(f"Error processing review: {e}")

            page_number += 1

        return redirect('reviews_list')
    else:
        return HttpResponse("Invalid Request")
def classify_sentiment(rating):
    if rating > 3.0:
        return 'Positive'
    elif rating < 3.0:
        return 'Negative'
    else:
        return 'Neutral'




def home_view(request):
    return render(request, 'reviews/home.html')


def reviews_list(request):
    reviews = Review.objects.all()


    sentiment_counts = reviews.values('sentiment').annotate(count=Count('sentiment'))

    #  the graph
    labels = [sentiment['sentiment'] for sentiment in sentiment_counts]
    counts = [sentiment['count'] for sentiment in sentiment_counts]

    plt.bar(labels, counts, color=['green', 'red', 'blue'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis of Reviews')
    plt.show()

    return render(request, 'reviews/reviews_list.html', {'reviews': reviews})