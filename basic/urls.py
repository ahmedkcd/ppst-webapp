from django.urls import path
from . import views
from .views import generate_test, test_page, login_view, dashboard, logout_view, test_intro, test_instructions
#individual
#from .views import login_view

from .views import take_test, get_responses, submit_response

app_name = "basic"

urlpatterns = [
    # path("compute/<int:value>", views.compute, name="compute"),
    # path("isprime/<int:value>", views.isprime, name="isprime"),
    path("generate-test/", generate_test, name="generate_test"),
    path("test-page/", test_page, name="test_page"),
    path('take-test/', take_test, name='take_test'),
    path('get-responses/', get_responses, name='get_responses'),
    path('submit-response/', submit_response, name='submit_responses'),
    #individual
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    #ppst
    path("test/intro/", test_intro, name="test_intro"),
    path("test/instructions/", views.test_instructions, name="test_instructions"),
    path('generate-test/', generate_test, name='generate_test'),
    path('test-page/', test_page, name='test_page'),

]
