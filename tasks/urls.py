from django.urls import path
from . import views

app_name="tasks"

urlpatterns = [
    path("listnotifications/<str:username>/", views.listnotifications, name="listnotifications"),
]