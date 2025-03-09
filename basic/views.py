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
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

#from .models import Response
#from .models import TestSession, Stimuli
from basic.models import Response, TestSession, Stimuli

#individual
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def test_page(request):
    return render(request, "basic/test_page.html")


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

    for i in range(12):
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

# individual programming hw - Functional login and dashboard
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(f"DEBUG: Attempting login with {username}:{password}")

        user = authenticate(username=username, password=password)
        if user is not None:
            print("DEBUG: Authentication successful")
            login(request, user)
            return redirect("basic:dashboard")  # redirects to the dashboard
        else:
            print("DEBUG: Authentication failed")  # more debugging
            return render(request, "basic/login.html", {"error": "Invalid credentials"})

    return render(request, "basic/login.html")


# Dashboard View that is accessible after login
@login_required
def dashboard(request):
    return render(request, "basic/dashboard.html", {"doctor_name": request.user.username})

def logout_view(request):
    logout(request)
    return redirect("basic:login")

# Start of PPST project work
def test_intro(request):
    return render(request, "basic/test_intro.html")

def test_instructions(request):
    return render(request, "basic/test_instructions.html")
