import json
import csv
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import User

from basic.models import TestSession, User, Response, Stimuli


def doctor_login_view(request):
    return render(request, 'basic/doctor_login.html')


def doctor_test_page(request):
    return render(request, 'basic/doctor_taketest.html')


def doctor_user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("basic:doctor-dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("basic:doctor-login")

    return render(request, "basic/doctor_login.html")

@login_required(login_url='/basic/')
def dashboard(request):
    doctor = request.user

    all_tests = TestSession.objects.filter(doctor=doctor)

    total_tests = all_tests.count()
    active_tests = all_tests.filter(status='active').count()
    pending_tests = all_tests.filter(status='pending').count()

    recent_tests = all_tests.filter(avg_latency__isnull=False).order_by('-created_at')[:10]
    last_10 = list(recent_tests[::-1])

    test_scores = [round(t.accuracy, 2) if t.accuracy is not None else 0 for t in last_10]
    test_dates = [t.created_at.strftime("%Y-%m-%d") for t in last_10]

    context = {
        'doctor_name': doctor.username,
        'total_tests': total_tests,
        'active_tests': active_tests,
        'pending_tests': pending_tests,
        'recent_tests': recent_tests,
        'test_scores': json.dumps(test_scores),
        'test_dates': json.dumps(test_dates),
    }

    return render(request, 'basic/dashboard.html', context)


@login_required(login_url='/basic/')
def doctor_dashboard(request):
    return render(request, 'basic/dashboard.html', {
        'doctor_name': request.user.username
    })


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
    total_tests = TestSession.objects.count()
    total_doctors = User.objects.filter(testsession__isnull=False).distinct().count()
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


def generate_test(request):
    age = request.GET.get("age")
    language = request.GET.get("language")
    if age is None:
        return JsonResponse({"error": "Age parameter is required."}, status=400)

    test_orders = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8],
        [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    selected_order = random.choice(test_orders)
    stimuli_list = list(Stimuli.objects.exclude(type="Practice"))
    ordered_stimuli = [stimuli_list[i] for i in selected_order]
    stimuli_order_str = ",".join(map(str, selected_order))

    test_session = TestSession.objects.create(
        doctor=request.user,
        age=age,
        language=language,
        stimuli_order=stimuli_order_str
    )

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
        "link": f"http://localhost:8000/basic/test/intro/?test_id={test_session.test_id}"
    })


@csrf_exempt
def record_responses_bulk(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            responses_data = data.get("responses", [])
            if not responses_data:
                return JsonResponse({"error": "No responses provided."}, status=400)

            with transaction.atomic():
                for response_entry in responses_data:
                    response = get_object_or_404(Response, response_id=response_entry.get("response_id"))
                    response.response = response_entry.get("response")
                    response.latency = response_entry.get("latency")
                    response.is_correct = response_entry.get("is_correct")
                    response.save()
                    test_session = response.test

                stats = test_session.response_set.aggregate(
                    avg_latency=models.Avg("latency"),
                    total_responses=models.Count("response_id"),
                    correct_responses=models.Count("response_id", filter=models.Q(is_correct=True))
                )
                test_session.avg_latency = stats["avg_latency"]
                test_session.accuracy = (stats["correct_responses"] / stats["total_responses"]) * 100 if stats["total_responses"] else 0
                test_session.save()

            return JsonResponse({"message": "Responses recorded successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


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

def forgot_password_view(request):
    return render(request, "basic/forgot_password.html")

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


@login_required(login_url='/basic/')
def doctor_dashboard(request):
    doctor = request.user

    # All tests by this doctor
    all_tests = TestSession.objects.filter(doctor=doctor)

    total_tests = all_tests.count()
    active_tests = all_tests.filter(status='active').count()  # Adjust if you use different status naming
    pending_tests = all_tests.filter(status='pending').count()

    recent_tests = all_tests.filter(avg_latency__isnull=False).order_by('-created_at')[:10]

    last_10 = list(all_tests.filter(avg_latency__isnull=False).order_by('-created_at')[:10][::-1])  # reverse for graph order
    test_scores = [round(t.accuracy, 2) if t.accuracy is not None else 0 for t in last_10]
    test_dates = [t.created_at.strftime("%Y-%m-%d") for t in last_10]

    context = {
        'doctor_name': doctor.username,
        'total_tests': total_tests,
        'active_tests': active_tests,
        'pending_tests': pending_tests,
        'recent_tests': recent_tests,
        'test_scores': json.dumps(test_scores),
        'test_dates': json.dumps(test_dates),
    }

    return render(request, 'basic/dashboard.html', context)



def test_intro(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_intro.html", {"test_id": test_id})


def test_instructions(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_instructions.html", {"test_id": test_id})


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


# Test Results View
# This view is for displaying the test results to the user after they complete their test.
def testresults(request):
    return render(request, "basic/testresults.html")

# Test Statistics View
# This view is for displaying the test statistics to the user.
@login_required(login_url='/basic/')
def test_statistics(request):
    return render(request, "basic/test_statistics.html")

# Register View
# This view is for handling user registration. It checks if the username already exists and creates a new user if not.
# It also logs in the user after successful registration.
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("basic:register")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("basic:dashboard")

    return render(request, "basic/register.html")