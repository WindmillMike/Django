from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("aplicatie_exemplu/", include("aplicatie_exemplu.urls")),
]
