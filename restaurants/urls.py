from django.urls import path

from . import views


urlpatterns = [
    path("top/<postal_code>/<category>/<price>", views.top_restaurants, name="top_restaurants"),
    path("review/<business_id>", views.get_reviews, name="get_reviews"),
    path("postalcodes", views.get_postal_codes, name="get_postal_codes"),
    path("restaurantlist", views.get_restaurants, name="get_restaurants"),
    path("aspect/<aspect>/<business_id>", views.get_aspect, name="get_aspect"),
]