from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("api/", include("api.urls")),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
