from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
    # path("login", views.login, name="login"),
    path("login", views.user_login, name="login"),
    path("dashboard", views.dashboard, name="dashboard"),

]