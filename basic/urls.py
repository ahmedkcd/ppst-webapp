from django.urls import path
from . import views
from .views import export_test_data

app_name="basic"

urlpatterns = [
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
   path("testresults/", views.testresults, name="testresults"),
   path("export_test_data/", views.export_test_data, name="export_test_data")
]