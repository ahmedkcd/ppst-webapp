# Create your views here.

# stimulus are hard coded

# pseudo ///
# first generate a new test model with user id and age
# then generate a response model for every stimulus
# link each response with a unique stimulus and that same test id

import json
import random

from django.db import models
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .models import Response
from .models import TestSession, Stimuli


def generate_test(request):
    age = request.GET.get("age", None)  # Default to None if not provided
    if age is None:
        return JsonResponse({"error": "Age parameter is required."}, status=400)

    test_session = TestSession.objects.create(
        doctor=request.user,
        age=age,
    )

    stimuli_list = list(Stimuli.objects.all())
    random.shuffle(stimuli_list)

    responses = []

    for i in range(24):
        stimulus = stimuli_list[i]
        response = Response.objects.create(
            test=test_session,
            stim=stimulus,
        )
        responses.append({
            "response_id": response.response_id,
            "stimulus": stimulus.stim_id,
        })

    return JsonResponse({"test_id": test_session.test_id, "responses": responses})


# a single json file that holds all the responses latencies everything, then a single view that parses and updates the db
# it would be best to just have one request for all the responses after a test is recorded


@csrf_exempt  # Disable CSRF for simplicity (use proper authentication in production)
def record_responses_bulk(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            responses_data = data.get("responses", [])

            if not responses_data:
                return JsonResponse({"error": "No responses provided."}, status=400)

            with transaction.atomic():  # Ensures all updates succeed or none do
                for response_entry in responses_data:
                    response_id = response_entry.get("response_id")
                    user_response = response_entry.get("response")
                    latency = response_entry.get("latency")
                    is_correct = response_entry.get("is_correct")

                    response = get_object_or_404(Response, response_id=response_id)
                    response.response = user_response
                    response.latency = latency
                    response.is_correct = is_correct
                    response.save()

                    test_session = response.test

                stats = test_session.response_set.aggregate(
                    avg_latency=models.Avg("latency"),
                    total_responses=models.Count("response_id"),
                    correct_responses=models.Count("response_id", filter=models.Q(is_correct=True))
                )
                test_session.avg_latency = stats["avg_latency"]
                test_session.accuracy = (stats["correct_responses"] / stats["total_responses"]) * 100 if stats[
                    "total_responses"] else 0
                test_session.save()

            return JsonResponse({"message": "Responses recorded successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

def test_statistics(request, test_id):
    test_session = get_object_or_404(TestSession, test_id=test_id)
    responses = Response.objects.filter(test=test_session)

    total_responses = responses.count()
    correct_responses = responses.filter(is_correct=True).count()
    avg_latency = responses.aggregate(models.Avg('latency'))['latency__avg'] or 0

    accuracy = (correct_responses / total_responses) * 100 if total_responses else 0

    chart_data = {
        'labels': ['Accuracy (%)', 'Avg Latency (ms)', 'Total Responses'],
        'values': [accuracy, avg_latency, total_responses]
    }

    # Pass the chart_data to the template
    return render(request, 'basic/test_statistics.html', {'test_id': test_id, 'chart_data': chart_data})





