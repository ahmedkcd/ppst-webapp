from django.urls import path

from .views import (
    generate_test, test_page, take_test, 
    get_responses, submit_response, user_login, 
    dashboard, results, statistics, newtest, 
    base, landing, logout_view
)

app_name = "basic"

urlpatterns = [
    # path("compute/<int:value>", views.compute, name="compute"),
    # path("isprime/<int:value>", views.isprime, name="isprime"),

    # User-related paths
    path("login", user_login, name="login"),
    path("dashboard", dashboard, name='dashboard'),
    path("results", results, name='results'),
    path("statistics", statistics, name='statistics'),
    path("newtest", newtest, name="newtest"),
    path("base", base, name="base"),
    path("", landing, name='landing'),
    path('logout', logout_view, name='logout'),

    # Test-related paths
    path('generate-test/', generate_test, name='generate_test'),
    path('test-page/', test_page, name='test_page'),
    path('take-test/', take_test, name='take_test'),
    path('get-responses/', get_responses, name='get_responses'),
    path('submit-response/', submit_response, name='submit_responses'),
]
