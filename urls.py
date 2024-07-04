from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('scrape_reviews/', views.scrape_reviews_view, name='scrape_reviews'),
    path('reviews_list/<encoded_product_url>/', views.reviews_list, name='reviews_list'),
]
