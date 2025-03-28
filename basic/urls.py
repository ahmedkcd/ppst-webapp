from django.urls import path

from .views import generate_test, test_page, take_test, get_responses, submit_response, test_statistics

app_name = "basic"

urlpatterns = [
    path("test_statistics/<int:test_id>/", test_statistics, name="test_statistics"),
    path('generate-test/', generate_test, name='generate_test'),
    path('test-page/', test_page, name='test_page'),
    path('take-test/', take_test, name='take_test'),
    path('get-responses/', get_responses, name='get_responses'),
    path('submit-response/', submit_response, name='submit_responses'),
]
