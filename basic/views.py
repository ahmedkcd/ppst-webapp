import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from django.views.decorators.csrf import csrf_exempt

from basic.models import TestSession, User, Stimuli, Response


# Authentication Views
def login_view(request):
    return render(request, "basic/login.html")

def test_page(request):
    return render(request, "basic/test_page.html")

def take_test(request):
    return render(request, "basic/take_test.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("basic:dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("basic:login")

    return render(request, "basic/login.html")


@login_required(login_url="/basic/")
def dashboard(request):
    return render(request, "basic/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("basic:landing")


# Core Pages
def test_page(request):
    return render(request, "basic/take_test.html")


def results(request):
    test_sessions = TestSession.objects.filter(doctor=request.user)
    return render(request, "basic/results.html", {"test_sessions": test_sessions})


def statistics(request):
    return render(request, "basic/statistics.html")


def newtest(request):
    return render(request, "basic/newtest.html")


def base(request):
    return render(request, "basic/base.html")


def landing(request):
    total_tests = TestSession.objects.count()
    total_doctors = User.objects.filter(testsession__isnull=False).distinct().count()

    return render(
        request,
        "basic/landing.html",
        {"total_tests": total_tests, "total_doctors": total_doctors},
    )


# Test Generation and Response Handling
@login_required
def generate_test(request):
    age = request.GET.get("age")
    language = request.GET.get("language")
    if not age:
        return JsonResponse({"error": "Age parameter is required."}, status=400)

    test_orders = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8],
        [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]

    selected_order = random.choice(test_orders)
    stimuli_list = list(Stimuli.objects.all())
    if len(stimuli_list) < 12:
        return JsonResponse({"error": "Not enough stimuli available."}, status=500)

    ordered_stimuli = [stimuli_list[i] for i in selected_order]
    stimuli_order_str = ",".join(map(str, selected_order))

    test_session = TestSession.objects.create(
        doctor=request.user, age=age, language=language, stimuli_order=stimuli_order_str
    )

    responses = [
        {
            "response_id": Response.objects.create(test=test_session, stim=stim).response_id,
            "stimulus": stim.stim_id,
        }
        for stim in ordered_stimuli
    ]

    return JsonResponse(
        {
            "test_id": test_session.test_id,
            "language": test_session.language,
            "stimuli_order": stimuli_order_str,
            "responses": responses,
            "link": f"http://localhost:8000/basic/take-test/?test_id={test_session.test_id}",
        }
    )


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
                    response = get_object_or_404(Response, response_id=response_entry["response_id"])
                    response.response = response_entry.get("response")
                    response.latency = response_entry.get("latency")
                    response.is_correct = response_entry.get("is_correct")
                    response.save()

                    test_session = response.test

                stats = test_session.response_set.aggregate(
                    avg_latency=models.Avg("latency"),
                    total_responses=models.Count("response_id"),
                    correct_responses=models.Count("response_id", filter=models.Q(is_correct=True)),
                )
                test_session.avg_latency = stats["avg_latency"]
                test_session.accuracy = (
                    (stats["correct_responses"] / stats["total_responses"]) * 100
                    if stats["total_responses"]
                    else 0
                )
                test_session.save()

            return JsonResponse({"message": "Responses recorded successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def get_responses(request):
    test_id = request.GET.get("test_id")
    responses = Response.objects.filter(test_id=test_id).select_related("stim")

    return JsonResponse(
        {"responses": [{"response_id": r.response_id, "stimulus_text": r.stim.stimulus} for r in responses]}
    )


@csrf_exempt
def submit_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response = get_object_or_404(Response, pk=data.get("response_id"))

            response.response = data.get("response")
            response.latencies = data.get("latencies", "")
            response.is_correct = response.response == response.stim.correct_response
            response.save()

            return JsonResponse({"status": "success"})
        except Response.DoesNotExist:
            return JsonResponse({"error": "Response not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)
