from django.urls import path

from .views import (
    generate_test, test_page, login_view, dashboard, logout_view,
    test_intro, test_instructions, take_test, get_responses, submit_response, practice_test,
    get_practice_responses, practice_countdown, practice_transition, test_complete, doctor_dashboard,
    doctor_logout_view, doctor_newtest, doctor_results, doctor_statistics, doctor_test_page,
    doctor_user_login, base, landing, testresults, export_test_data, test_statistics
)

app_name = "basic"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("test/intro/", test_intro, name="test_intro"),
    path("test/instructions/", test_instructions, name="test_instructions"),
    path("generate-test/", generate_test, name="generate_test"),
    path("test-page/", test_page, name="test_page"),
    path("take-test/", take_test, name="take_test"),
    path("get-responses/", get_responses, name="get_responses"),
    path("submit-response/", submit_response, name="submit_responses"),
    # Practice seg
    path("practice-test/", practice_test, name="practice_test"),
    path("get-practice-responses/", get_practice_responses, name="get_practice_responses"),
    path("practice-countdown/", practice_countdown, name="practice_countdown"),
    path("practice/transition/", practice_transition, name="practice-transition"),
    path("test/complete/", test_complete, name="test_complete"),

    path("doctor-login", doctor_user_login, name="doctor-login"),
    path("doctor-dashboard", doctor_dashboard, name='doctor-dashboard'),
    path("doctor-results", doctor_results, name='doctor-results'),
    path("doctor-statistics", doctor_statistics, name='doctor-statistics'),
    path("doctor-newtest", doctor_newtest, name="doctor-newtest"),
    path("base", base, name="base"),
    path("", landing, name='landing'),
    path('doctor-logout', doctor_logout_view, name='doctor-logout'),
    path('doctor-testpage', doctor_test_page, name='doctor-testpage'),
    path("testresults/", testresults, name="testresults"),
    path("export_test_data/", export_test_data, name="export_test_data"),
    path("test_statistics/<str:test_id>/", test_statistics, name="test_statistics")
    ]
