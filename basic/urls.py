from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
   path("test_statistics/<int:test_id>/", views.test_statistics, name="test_statistics"),
]