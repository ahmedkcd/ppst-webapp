# Create your views here.

# stimulus are hard coded

# pseudo ///
# first generate a new test model with user id and age
# then generate a response model for every stimulus
# link each response with a unique stimulus and that same test id

import json
import random

from django import forms
from django.db import models
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

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

def get_preset_stimuli():
    """Retrieve all stimuli from the database as a list of tuples for dropdown selection."""
    try:
        stimuli = list(Stimuli.objects.values_list('stimulus', 'stimulus'))  # (stimulus, stimulus)
        if not stimuli:
            print("No stimuli in the database!")
        return stimuli
    except Exception as e:
        print(f"Error fetching stimuli: {e}")  
        return []  # Return an empty list instead of breaking the form
    
# Define a response form using dynamically loaded stimuli
class StimulusResponseForm(forms.Form):
    stimulus = forms.ChoiceField(choices=[])
    response = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter response"}))

    def __init__(self, *args, **kwargs):
        super(StimulusResponseForm, self).__init__(*args, **kwargs)
        self.fields['stimulus'].choices = get_preset_stimuli()

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def testpage(request):
    form = StimulusResponseForm(request.GET or None)  # Use GET, since the form submits with GET
    selected_stimulus = request.GET.get("stimulus", None)  # Get stimulus directly from query parameters

    return render(request, "basic/testpage.html", {
        "form": form,
        "selected_stimulus": selected_stimulus,  # This will pass stimulus to the template
    })



@require_POST
def testpage_response(request):
    times = request.POST['times']
    
    # Split times and filter out any empty strings
    responses = [response for response in times.split(" ") if response.strip()]

    # Ensure there are at least two responses to calculate latency
    if len(responses) < 2:
        return JsonResponse({"error": "Insufficient data."}, status=400)

    previous = int(responses[0].split(":")[1])
    responses.pop(0)
    answer = "Server received: "

    for response in responses:
        values = response.split(':')
        button = values[0]
        latency = (int(values[1]) - previous) / 1000  # Convert to seconds
        previous = int(values[1])
        answer = f"{answer} Button {button} after a latency of {latency} seconds. "

    return render(request, "basic/times.html", {
        'answer': answer,
    })
