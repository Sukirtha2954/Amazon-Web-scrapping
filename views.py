import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Review


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
        base_url = 'https://www.amazon.in/Samsung-Galaxy-Smartphone-Titanium-Storage/product-reviews/B0CQYGF1QY/ref=cm_cr_getr_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=1'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        page_number = 1
        while True:
            url = base_url.format(page_number)
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            reviews = soup.find_all('div', {'data-hook': 'review'})

            print(f"Number of reviews found on page {page_number}: {len(reviews)}")  # Debugging

            if not reviews:
                # No more reviews found, exit the loop
                break

            for review in reviews:
                try:
                    title = review.find('a', {'data-hook': 'review-title'}).text.strip()
                    content = review.find('span', {'data-hook': 'review-body'}).text.strip()
                    rating = float(
                        review.find('i', {'data-hook': 'review-star-rating'}).text.split()[0].replace(',', '.'))

                    print(f"Title: {title}, Content: {content}, Rating: {rating}")  # Debugging

                    Review.objects.create(
                        title=title,
                        content=content,
                        rating=rating,
                    )
                except Exception as e:
                    print(f"Error processing review: {e}")  # Debugging

            page_number += 1

        return redirect('reviews_list')
    else:
        return HttpResponse("Invalid Request")


def home_view(request):
    return render(request, 'reviews/home.html')


def reviews_list(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/reviews_list.html', {'reviews': reviews})
