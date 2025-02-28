# Create your views here.

# every test needs 6 4 span and 6 5 span tests
# to generate a test get 6 random 4 span and 6 random 5 span models
# then create a new test id and 12 response tests that link to each stimilus
# we have the same stimulus so just shuffle the order for each type
# then link the responses to the test id
# so itll go 12 stimulus -> 12 responses -> 1 test

# stimulus are hard coded

# pseudo /// for every stimulus with span of 5 and type numeric
# first generate a new test model with user id and age
# then generate a response model for every stimulus
# link each response with a unique stimulus and that same test id

import random

from django.http import JsonResponse

from .models import TestSession, Stimuli, Response


def generate_test(request):
    test_session = TestSession.objects.create(
        doctor=request.user,
        age=request.age,
    )

    stimuli_list = list(Stimuli.objects.all())
    random.shuffle(stimuli_list)

    responses = []

    for i in range(24):
        stimulus = stimuli_list[i]
        response = Response.objects.create(
            test=test_session.test_id,
            stim=stimulus.stim_id,
        )
        responses.append({
            "response_id": response.response_id,
            "stimulus": stimulus.stim_id,
        })

    return JsonResponse({"test_id": test_session.test_id, "responses": responses})
