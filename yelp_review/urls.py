from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("restaurants/", include("restaurants.urls")),
    path("admin/", admin.site.urls),
]
