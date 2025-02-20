from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
    path("compute/<int:value>", views.compute, name="compute"),
    path("hello/", views.hello, name="hello"),
    path("isprime/<int:number>", views.isprime, name="isprime"),
]