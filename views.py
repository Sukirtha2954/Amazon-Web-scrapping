import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count
import matplotlib.pyplot as plt
import io
import base64
import re
import urllib.parse
import pandas as pd
from django.utils.html import escape
from .models import Review

# Initialize the TF-IDF vectorizer 
# from sklearn.feature_extraction.text import TfidfVectorizer

# Sample labeled dataset for training (not needed for star-based classification)
# sample_data = [
#     ("4.0 out of 5 stars About s24 ultra", "Positive"),
#     ("5.0 out of 5 stars One of the best smartphones available as for 2024.", "Positive"),
#     ("5.0 out of 5 stars One of the most excellent ", "Positive"),
#     ("2.0 out of 5 stars", "Neutral"),
#     ("3.0 out of 5 stars", "Neutral")
# ]

# df = pd.DataFrame(sample_data, columns=['review', 'sentiment'])

# Split the data into training and testing sets (not needed for star-based classification)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the classifiers (not needed for star-based classification)
# rf_classifier = RandomForestClassifier()
# dt_classifier = DecisionTreeClassifier()

# rf_classifier.fit(X_train, y_train)
# dt_classifier.fit(X_train, y_train)

def extract_product_name(url):
    pattern = r'https://www\.amazon\.in/([^/]+)/'
    match = re.search(pattern, url)
    if match:
        return match.group(1).replace('-', ' ').title()
    return 'Product'

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "user1" and password == "adminrights":
            return redirect('scrape_reviews')
        else:
            return HttpResponse("Invalid login")
    return render(request, 'reviews/login.html')

def sanitize_content(content):
    return escape(content)

def classify_sentiment(stars):
    stars = float(stars)
    if stars <= 2.0:
        return 'Negative'
    elif stars == 3.0:
        return 'Neutral'
    elif stars > 3.0:
        return 'Positive'
    else:
        return 'Unknown'

def scrape_reviews_view(request):
    if request.method == "POST":
        product_url = request.POST.get('product_url')
        base_url = product_url + '&pageNumber={}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        page_number = 1
        total_reviews = 0
        Review.objects.all().delete()  # Remove this line if you don't want to delete existing reviews

        while total_reviews < 193:
            url = base_url.format(page_number)
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            reviews = soup.find_all('div', {'data-hook': 'review'})

            if not reviews:
                break

            for review in reviews:
                try:
                    # Extract review details
                    stars = review.find('span', {'class': 'a-icon-alt'}).text.split()[0]
                    title = review.find('a', {'data-hook': 'review-title'}).text.strip()
                    content = review.find('span', {'data-hook': 'review-body'}).text.strip()

                    # Classify sentiment based on stars
                    sentiment_label = classify_sentiment(stars)

                    # Sanitize the title and content
                    title = sanitize_content(title)
                    content = sanitize_content(content)

                    Review.objects.create(
                        title=title,
                        content=content,
                        sentiment=sentiment_label,
                        url=product_url
                    )
                    total_reviews += 1
                    print(f"Saved review: {title} with sentiment {sentiment_label}")
                except Exception as e:
                    print(f"Error processing review: {e}")

            page_number += 1

        encoded_product_url = urllib.parse.quote(product_url, safe='')
        return redirect('reviews_list', encoded_product_url=encoded_product_url)

    else:
        return render(request, 'reviews/scrape_reviews.html')

def home_view(request):
    return render(request, 'reviews/home.html')

def reviews_list(request, encoded_product_url):
    try:
        product_url = urllib.parse.unquote(encoded_product_url)
        reviews = Review.objects.filter(url=product_url)

        product_name = extract_product_name(product_url)

        # Categorize reviews by sentiment
        positive_reviews = reviews.filter(sentiment='Positive')
        negative_reviews = reviews.filter(sentiment='Negative')
        neutral_reviews = reviews.filter(sentiment='Neutral')

        # Collect review titles and sentiments for table display
        positive_analyzed_reviews = positive_reviews.values('title', 'sentiment')
        negative_analyzed_reviews = negative_reviews.values('title', 'sentiment')
        neutral_analyzed_reviews = neutral_reviews.values('title', 'sentiment')

        # Generate overall sentiment analysis graph
        sentiment_counts = reviews.values('sentiment').annotate(count=Count('sentiment'))
        labels = [sentiment['sentiment'] for sentiment in sentiment_counts]
        counts = [sentiment['count'] for sentiment in sentiment_counts]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(labels, counts, color=['green', 'red', 'blue'])
        ax.set_xlabel('Sentiment')
        ax.set_ylabel('Count')
        ax.set_title(f'Sentiment Analysis of Reviews for {product_name}')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # Save plot to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()

        # Convert for embedding in HTML
        plot_base64 = base64.b64encode(plot_data).decode('utf-8')
        plt.close()

        # Generate positive reviews graph
        positive_titles = [review['title'] for review in positive_analyzed_reviews][:20]

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(range(len(positive_titles)), [1] * len(positive_titles), color='green')  # Plotting 1 for each word
        ax.set_yticks(range(len(positive_titles)))
        ax.set_yticklabels(positive_titles)
        ax.set_xlabel('Top Analyzed Words')
        ax.set_title('Top 20 Positive Analyzed Words')
        plt.tight_layout()



        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()

        positive_plot_base64 = base64.b64encode(plot_data).decode('utf-8')
        plt.close()


        # Generate negative reviews graph
        negative_titles = [review['title'] for review in negative_analyzed_reviews][:20]

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(range(len(negative_titles)), [1] * len(negative_titles), color='red')  # Plotting 1 for each word
        ax.set_yticks(range(len(negative_titles)))
        ax.set_yticklabels(negative_titles)
        ax.set_xlabel('Top Analyzed Words')
        ax.set_title('Top 20 Negative Analyzed Words')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()

        negative_plot_base64 = base64.b64encode(plot_data).decode('utf-8')
        plt.close()

        # Generate neutral reviews graph
        # Generate negative reviews graph
        negative_titles = [review['title'] for review in negative_analyzed_reviews][:20]

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(range(len(negative_titles)), [1] * len(negative_titles), color='red')  # Plotting 1 for each word
        ax.set_yticks(range(len(negative_titles)))
        ax.set_yticklabels(negative_titles)
        ax.set_xlabel('Top Analyzed Words')
        ax.set_title('Top 20 Negative Analyzed Words')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()

        neutral_plot_base64 = base64.b64encode(plot_data).decode('utf-8')
        plt.close()

        return render(request, 'reviews/reviews_list.html', {
            'positive_analyzed_reviews': positive_analyzed_reviews,
            'negative_analyzed_reviews': negative_analyzed_reviews,
            'neutral_analyzed_reviews': neutral_analyzed_reviews,
            'product_name': product_name,
            'plot_base64': plot_base64,
            'positive_plot_base64': positive_plot_base64,
            'negative_plot_base64': negative_plot_base64,
            'neutral_plot_base64': neutral_plot_base64,
        })
    except Exception as e:
        print(f"Error in reviews_list view: {e}")
        return HttpResponse("An error occurred while processing the reviews")
