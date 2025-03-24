from django.urls import path
from . import views

app_name="basic"

urlpatterns = [
   # path("compute/<int:value>", views.compute, name="compute"),
   # path("isprime/<int:value>", views.isprime, name="isprime"),
    # path("login", views.login, name="login"),
    path("login", views.user_login, name="login"),
    path("dashboard", views.dashboard, name='dashboard'),
    path("results", views.results, name='results'),
    path("statistics", views.statistics, name='statistics'),
    path("newtest", views.newtest,name="newtest"),
    path("base",views.base,name="base"),
    path("", views.landing, name='landing'),
    path('logout', views.logout_view, name='logout'),
    path('testpage', views.test_page, name='testpage'),
    
    

]