# Create your views here.

# stimulus are hard coded

# pseudo ///
# first generate a new test model with user id and age
# then generate a response model for every stimulus
# link each response with a unique stimulus and that same test id

import json

from django.db import models
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def test_page(request):
    return render(request, "basic/test_page.html")

def take_test(request):
    return render(request, "basic/take_test.html")


import random
from django.contrib.auth.decorators import login_required
from .models import TestSession, Stimuli


@login_required
def generate_test(request):
    age = request.GET.get("age")
    language = request.GET.get("language")
    if age is None:
        return JsonResponse({"error": "Age parameter is required."}, status=400)

    # Define preset test orders (4 possible sequences)
    test_orders = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8],
        [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]

    # Pick a random test order
    selected_order = random.choice(test_orders)

    # Fetch stimuli and apply the selected order
    stimuli_list = list(Stimuli.objects.all())
    if len(stimuli_list) < 12:
        return JsonResponse({"error": "Not enough stimuli available."}, status=500)

    ordered_stimuli = [stimuli_list[i] for i in selected_order]

    # Store the order as a comma-separated string
    stimuli_order_str = ",".join(map(str, selected_order))

    # Create the test session
    test_session = TestSession.objects.create(
        doctor=request.user,
        age=age,
        language=language,
        stimuli_order=stimuli_order_str  # Store as text
    )

    # Generate responses
    responses = []
    for stimulus in ordered_stimuli:
        response = Response.objects.create(
            test=test_session,
            stim=stimulus,
        )
        responses.append({
            "response_id": response.response_id,
            "stimulus": stimulus.stim_id,
        })

    return JsonResponse({
        "test_id": test_session.test_id,
        "language": test_session.language,
        "stimuli_order": stimuli_order_str,  # Return order for verification
        "responses": responses,
        "link" : f"http://localhost:8000/basic/take-test/?test_id={test_session.test_id}"
    })


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

from django.http import JsonResponse
from .models import Response

def get_responses(request):
    test_id = request.GET.get("test_id")
    responses = Response.objects.filter(test_id=test_id).select_related('stim')

    data = [
        {"response_id": r.response_id, "stimulus_text": r.stim.stimulus}
        for r in responses
    ]

    return JsonResponse({"responses": data})

@csrf_exempt
def submit_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        response_id = data.get("response_id")
        user_response = data.get("response")
        latencies = data.get("latencies", "")

        try:
            response = Response.objects.get(pk=response_id)
            response.response = user_response
            response.latencies = latencies
            response.is_correct = (user_response == response.stim.correct_response)
            response.save()
            return JsonResponse({"status": "success"})
        except Response.DoesNotExist:
            return JsonResponse({"error": "Response not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)