from django.urls import path

from .views import (
    generate_test, logout_view,
    test_intro, test_instructions, take_test, get_responses, practice_test,
    get_practice_responses, practice_countdown, practice_transition, test_complete, doctor_dashboard,
    submit_all_responses,
    doctor_logout_view, doctor_newtest, doctor_results, doctor_statistics,
    doctor_user_login, base, landing, export_test_data, test_statistics,
    test_intro_sp, test_instructions_sp, practice_test_sp, take_test_sp, practice_countdown_sp, practice_transition_sp,
    test_complete_sp, get_practice_responses_sp, aggregated_statistics
)

app_name = "basic"

urlpatterns = [

    # English Test
    path("test/intro/", test_intro, name="test_intro"),
    path("test/instructions/", test_instructions, name="test_instructions"),
    path("take-test/", take_test, name="take_test"),
    path("get-responses/", get_responses, name="get_responses"),
    path("submit-all-responses/", submit_all_responses, name="submit_all_responses"),
    path("practice-test/", practice_test, name="practice_test"),
    path("get-practice-responses/", get_practice_responses, name="get_practice_responses"),
    path("practice-countdown/", practice_countdown, name="practice_countdown"),
    path("practice/transition/", practice_transition, name="practice-transition"),
    path("test/complete/", test_complete, name="test_complete"),

    # Dashboard
    path("doctor-login", doctor_user_login, name="doctor-login"),
    path("doctor-dashboard", doctor_dashboard, name='doctor-dashboard'),
    path("doctor-results", doctor_results, name='doctor-results'),
    path("doctor-statistics", doctor_statistics, name='doctor-statistics'),
    path("doctor-newtest", doctor_newtest, name="doctor-newtest"),
    path("generate-test/", generate_test, name="generate_test"),
    path("base", base, name="base"),
    path("", landing, name='landing'),
    path('doctor-logout', doctor_logout_view, name='doctor-logout'),
    path("logout/", logout_view, name="logout"),
    path("export_test_data/", export_test_data, name="export_test_data"),
    path("test_statistics/<str:test_id>/", test_statistics, name="test_statistics"),
    path('aggregated-statistics/', aggregated_statistics, name='aggregated-statistics'),

    # Spanish Test
    path("test/intro-sp/", test_intro_sp, name="test_intro_sp"),
    path("test/instructions-sp/", test_instructions_sp, name="test_instructions_sp"),
    path("take-test-sp/", take_test_sp, name="take_test_sp"),
    path("practice-test-sp/", practice_test_sp, name="practice_test_sp"),
    path("practice-countdown-sp/", practice_countdown_sp, name="practice_countdown_sp"),
    path("practice/transition-sp/", practice_transition_sp, name="practice-transition_sp"),
    path("test/complete-sp/", test_complete_sp, name="test_complete_sp"),
    path("get-practice-responses-sp", get_practice_responses_sp, name="get_practice_responses_sp"),
]
