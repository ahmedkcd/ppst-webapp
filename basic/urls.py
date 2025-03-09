from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
<<<<<<< HEAD
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
=======
    path("compute/<int:value>", views.compute, name="compute"),
    path("hello/", views.hello, name="hello"),
    path("isprime/<int:number>", views.isprime, name="isprime"),
>>>>>>> djangostarter/Amyr-Final-Prog-Branch
]