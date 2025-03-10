from django.urls import path
from . import views
from .views import generate_test, test_page, login_view, dashboard, logout_view, test_introduction, test_instructions
#Final Individual Project - Doctor Dashboard with Logout Out Functionality
#from .views import login_view

app_name = "basic"

urlpatterns = [

    # path("compute/<int:value>", views.compute, name="compute"),
    # path("isprime/<int:value>", views.isprime, name="isprime"),
    path("generate-test/", generate_test, name="generate_test"),
    path("test-page/", test_page, name="test_page"),
    
   
   
    path('dashboard/', views.dashboard, name='dashboard'),
    path("login/", views.login_view, name="login"),  # Add this!
    path("logout/", views.logout_view, name="logout"),

    
    
    #ppst - part of tbhe project 
    path("testing/introduction/", views.test_introduction, name="test_introduction"),
    path("testing/instructions/", views.test_instructions, name="test_instructions"),
]