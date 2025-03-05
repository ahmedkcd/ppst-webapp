from django.urls import path

from .views import generate_test, test_page

app_name = "basic"

urlpatterns = [
    # path("compute/<int:value>", views.compute, name="compute"),
    # path("isprime/<int:value>", views.isprime, name="isprime"),
    path('generate-test/', generate_test, name='generate_test'),
    path('test-page/', test_page, name='test_page'),
]
