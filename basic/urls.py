from django.urls import path
from .views import generate_test, test_page, login_view, dashboard, logout_view
#individual
#from .views import login_view

app_name = "basic"

urlpatterns = [
    # path("compute/<int:value>", views.compute, name="compute"),
    # path("isprime/<int:value>", views.isprime, name="isprime"),
    path("generate-test/", generate_test, name="generate_test"),
    path("test-page/", test_page, name="test_page"),
    #individual
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
]
