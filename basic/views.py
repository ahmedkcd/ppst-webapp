import csv
import json
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from basic.models import User


def doctor_login_view(request):
    return render(request, 'basic/doctor_login.html')


def doctor_test_page(request):
    return render(request, 'basic/doctor_taketest.html')


def doctor_user_login(request):
    if request.method == "POST":
        # Getting the username and password in the form post in the html page/
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Authentication is successful
            login(request, user)
            return redirect("basic:doctor-dashboard")  # Redirecting to the dashboard
        else:
            # Authentication is denied
            messages.error(request, "Invalid username or password")
            return  redirect("basic:doctor-login") # Redirecting to the login page, when refreshed

    return render(request, "basic/doctor_login.html")


@login_required(login_url='/basic/')
def doctor_dashboard(request):
    return render(request, 'basic/doctor_dashboard.html')
    
@login_required(login_url='/basic/')
def doctor_results(request):
    test_sessions = TestSession.objects.filter(doctor=request.user)
    return render(request, 'basic/doctor_results.html', {'test_sessions': test_sessions})
    
@login_required(login_url='/basic/')
def doctor_statistics(request):
    return render(request, 'basic/doctor_statistics.html')
    
@login_required(login_url='/basic/')
def doctor_newtest(request):
    return render(request, "basic/doctor_newtest.html")

def base(request):
    return render(request, "basic/base.html")

def landing(request):
     total_tests = TestSession.objects.count()  # Count all test sessions
     total_doctors = User.objects.filter(testsession__isnull=False).distinct().count()  # Count unique doctors with tests

     return render(request, "basic/landing.html", {
        "total_tests": total_tests,
        "total_doctors": total_doctors,
    })
def doctor_logout_view(request):
    logout(request)  
    return redirect('basic:landing') 


def test_page(request):
    return render(request, "basic/test_page.html")


def take_test(request):
    test_id = request.GET.get("test_id")
    if not test_id:
        return HttpResponse("Error: Test ID missing", status=400)

    test = get_object_or_404(TestSession, pk=test_id)
    return render(request, "basic/take_test.html", {"test": test})


import random
from django.contrib.auth.decorators import login_required
from .models import TestSession, Stimuli


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
    stimuli_list = list(Stimuli.objects.exclude(type="Practice"))

    ordered_stimuli = [stimuli_list[i] for i in selected_order]

    # Store the order as a comma-separated string
    stimuli_order_str = ",".join(map(str, selected_order))

    test_uuid = str(uuid.uuid4())

    # Create the test session
    test_session = TestSession.objects.create(
        doctor=request.user,
        age=age,
        language=language,
        stimuli_order=stimuli_order_str,
        test_id=test_uuid,
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

    test_link = f"http://localhost:8000/basic/test/intro/?test_id={test_uuid}"

    return JsonResponse({
        "message": "Test generated successfully.",
        "link": test_link,
        "copy_paste": f"Copy this link to access the test:\n{test_link}"
    })


def test_statistics(request, test_id):
    test_session = get_object_or_404(TestSession, test_id=test_id)
    responses = Response.objects.filter(test=test_session)

    total_responses = responses.count()
    correct_responses = responses.filter(is_correct=True).count()
    avg_latency = responses.aggregate(models.Avg('latencies'))['latencies__avg'] or 0

    accuracy = (correct_responses / total_responses) * 100 if total_responses else 0

    chart_data = {
        'labels': ['Accuracy (%)', 'Avg Latency (ms)', 'Total Responses'],
        'values': [accuracy, avg_latency, total_responses]
    }

    # Pass the chart_data to the template
    return render(request, 'basic/test_statistics.html', {'test_id': test_id, 'chart_data': chart_data})


@csrf_exempt
def submit_all_responses(request):
    if request.method == "POST":
        data = json.loads(request.body)
        for item in data["responses"]:
            response = Response.objects.get(response_id=item["response_id"])
            response.response = item["response"]
            response.latencies = item["latencies"]
            response.is_correct = (item["response"] == response.stim.correct_response)
            response.save()
        return JsonResponse({"status": "success"})


from django.http import JsonResponse
from .models import Response


def get_responses(request):
    test_id = request.GET.get("test_id")
    responses = Response.objects.filter(test_id=test_id).select_related('stim')

    data = [
        {"response_id": r.response_id, "stimulus_text": r.stim.stimulus, "stimulus_type": r.stim.type}
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


# practice segment work
def practice_test(request):
    test_id = request.GET.get("test_id")

    return render(request, "basic/practice_test.html", {"test_id": test_id})


def get_practice_responses(request):
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


def export_test_data(request):
    test_id = request.GET.get("test_id")
    responses = Response.objects.filter(test_id=test_id).select_related("stim")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="test_{test_id}_data.csv"'

    writer = csv.writer(response)

    writer.writerow(["Response ID", "Stimulus", "User Response", "Correct Response", "Is Correct", "Latencies"])

    for resp in responses:
        writer.writerow([
            resp.response_id,
            resp.stim.stimulus,
            resp.response,
            resp.stim.correct_response,
            "Yes" if resp.is_correct else "No",
            resp.latencies
        ])

    return response


def testresults(request):
    test_sessions = TestSession.objects.all()  # Retrieve all test sessions
    return render(request, "basic/testresults.html", {"test_sessions": test_sessions})
