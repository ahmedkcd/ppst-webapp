from django.urls import path
from .views import (
    generate_test, test_page, login_view, dashboard, logout_view,
    test_intro, test_instructions, take_test, get_responses, submit_response, start_test
)

app_name = "basic"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("test/intro/", test_intro, name="test_intro"),
    path("test/instructions/", test_instructions, name="test_instructions"),
    #merged matts urls
    path("generate-test/", generate_test, name="generate_test"),
    path("test-page/", test_page, name="test_page"),
    path("take-test/", take_test, name="take_test"),
    path("get-responses/", get_responses, name="get_responses"),
    path("submit-response/", submit_response, name="submit_responses"),
    path("start-test/<int:test_id>/", start_test, name="start_test"),
]
