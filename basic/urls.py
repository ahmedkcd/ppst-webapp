from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
   path("testpage/", views.testpage, name="testpage"),
   path("testpage_response/", views.testpage_response, name="testpage_response"),
]