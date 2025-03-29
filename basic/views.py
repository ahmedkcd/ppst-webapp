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
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def test_page(request):
    return render(request, "basic/test_page.html")

def take_test(request):
    return render(request, "basic/take_test.html")


import random
from django.contrib.auth.decorators import login_required
from .models import TestSession, Stimuli


# def take_test(request):
#     return render(request, "basic/take_test.html")
def take_test(request):
    test_id = request.GET.get("test_id")
    if not test_id:
        return HttpResponse("Error: Test ID missing", status=400)


    test = get_object_or_404(TestSession, pk=test_id)
    return render(request, "basic/take_test.html", {"test": test})


import random
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import TestSession, Stimuli, Response



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

        "link" : f"http://localhost:8000/basic/test/intro/?test_id={test_session.test_id}"
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

# indiv
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("basic:dashboard")
        else:
            return render(request, "basic/login.html", {"error": "Invalid credentials"})
    return render(request, "basic/login.html")

def logout_view(request):
    logout(request)
    return redirect("basic:login")

@login_required
def dashboard(request):
    return render(request, "basic/dashboard.html", {"doctor_name": request.user.username})

# def test_intro(request):
#     return render(request, "basic/test_intro.html")
def test_intro(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_intro.html", {"test_id": test_id})

# def test_instructions(request):
#     return render(request, "basic/test_instructions.html")
def test_instructions(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_instructions.html", {"test_id": test_id})

from django.http import HttpResponseRedirect

def start_test(request, test_id): # controls flow of test process in a single link
    step = request.GET.get("step", "intro")

    if step == "intro":
        return HttpResponseRedirect(f"/basic/test/instructions/?test_id={test_id}&step=instructions")
    elif step == "instructions":
        return HttpResponseRedirect(f"/basic/take-test/?test_id={test_id}&step=test")
    elif step == "test":
        return HttpResponseRedirect(f"/basic/take-test/?test_id={test_id}")
    else:
        return HttpResponseRedirect(f"/basic/test/intro/?test_id={test_id}&step=intro")
    
#practice segment work
def practice_test(request):
    test_id = request.GET.get("test_id")
    stimuli = Stimuli.objects.filter(type="Practice")[:2]  #fetch 2 practice stimuli
    practice_stimuli = [{"stimulus_text": s.stimulus} for s in stimuli]

    return render(request, "basic/practice_test.html", {"practice_stimuli": practice_stimuli, "test_id": test_id})

def get_practice_responses(request):
    test_id = request.GET.get("test_id")
    practice_stimuli = Stimuli.objects.filter(type="Practice")[:2]

    data = [{"stimulus_text": s.stimulus} for s in practice_stimuli]
    return JsonResponse({"responses": data})

def practice_countdown(request):
    test_id = request.GET.get("test_id")
    return render(request, "basic/practice_countdown.html", {"test_id": test_id})

def practice_transition(request):
    test_id = request.GET.get("test_id")
    return render(request, "basic/practice_transition.html", {"test_id": test_id})

def test_complete(request):
    return render(request, "basic/test_complete.html")

