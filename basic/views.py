import csv
import json
import uuid
import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.utils.dateparse import parse_date

from basic.models import TestSession, Stimuli, Response, User

# ----------------------------- AUTH & LANDING -----------------------------

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

def landing(request):
    total_tests = TestSession.objects.count()
    total_doctors = User.objects.filter(testsession__isnull=False).distinct().count()
    return render(request, "basic/landing.html", {
        "total_tests": total_tests,
        "total_doctors": total_doctors,
    })

def base(request):
    return render(request, "basic/base.html")

# ----------------------------- DOCTOR VIEWS -----------------------------

def doctor_login_view(request):
    return render(request, 'basic/doctor_login.html')

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
def doctor_dashboard(request):
    doctor = request.user
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    tests_qs = TestSession.objects.filter(doctor=doctor)
    if start_date:
        tests_qs = tests_qs.filter(date__gte=parse_date(start_date))
    if end_date:
        tests_qs = tests_qs.filter(date__lte=parse_date(end_date))

    total_tests = tests_qs.count()
    active_tests = tests_qs.filter(status="active").count()
    pending_tests = tests_qs.filter(status="pending").count()
    completed_tests = tests_qs.filter(status="completed").count()

    recent_tests = tests_qs.filter(accuracy__isnull=False).order_by("-date")[:10]
    labels = [test.date.strftime("%b %d") for test in recent_tests]
    scores = [round(test.accuracy or 0, 2) for test in recent_tests]
    latencies = [round(test.avg_latency or 0, 2) for test in recent_tests]

    stim_counts = Response.objects.filter(test__in=tests_qs).values("stim__type").annotate(count=Count("response_id"))
    stim_labels = [entry["stim__type"] for entry in stim_counts]
    stim_data = [entry["count"] for entry in stim_counts]

    context = {
        "user": doctor,
        "total_tests": total_tests,
        "active_tests": active_tests,
        "pending_tests": pending_tests,
        "completed_tests": completed_tests,
        "recent_tests": recent_tests,
        "labels": json.dumps(labels),
        "scores": json.dumps(scores),
        "latency_scores": json.dumps(latencies),
        "status_chart_labels": json.dumps(["Active", "Completed", "Pending"]),
        "status_chart_data": json.dumps([active_tests, completed_tests, pending_tests]),
        "stim_labels": json.dumps(stim_labels),
        "stim_data": json.dumps(stim_data),
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, 'basic/doctor_dashboard.html', context)

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

def doctor_logout_view(request):
    logout(request)
    return redirect('basic:landing')

def doctor_test_page(request):
    return render(request, 'basic/doctor_taketest.html')

# ----------------------------- TEST FLOW -----------------------------

@login_required
def dashboard(request):
    return render(request, "basic/dashboard.html", {"doctor_name": request.user.username})

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

    for stimulus in ordered_stimuli:
        Response.objects.create(test=test_session, stim=stimulus)

    return JsonResponse({
        "link": f"http://localhost:8000/basic/test/intro/?test_id={test_session.test_id}"
    })

def test_page(request):
    return render(request, "basic/test_page.html")

def take_test(request):
    test_id = request.GET.get("test_id")
    if not test_id:
        return HttpResponse("Error: Test ID missing", status=400)
    test = get_object_or_404(TestSession, pk=test_id)
    return render(request, "basic/take_test.html", {"test": test})

def test_intro(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_intro.html", {"test_id": test_id})

def test_instructions(request):
    test_id = request.GET.get("test_id", None)
    return render(request, "basic/test_instructions.html", {"test_id": test_id})

def test_complete(request):
    return render(request, "basic/test_complete.html")

# ----------------------------- PRACTICE -----------------------------

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

# ----------------------------- RESPONSES -----------------------------

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

def get_responses(request):
    test_id = request.GET.get("test_id")
    responses = Response.objects.filter(test_id=test_id).select_related('stim')
    data = [
        {"response_id": r.response_id, "stimulus_text": r.stim.stimulus, "stimulus_type": r.stim.type}
        for r in responses
    ]
    return JsonResponse({"responses": data})

# ----------------------------- STATS & EXPORT -----------------------------

def test_statistics(request, test_id):
    test_session = get_object_or_404(TestSession, test_id=test_id)
    responses = Response.objects.filter(test=test_session)

    total_responses = responses.count()
    correct_responses = responses.filter(is_correct=True).count()
    avg_latency = responses.aggregate(models.Avg('latencies'))['latencies__avg'] or 0
    accuracy = (correct_responses / total_responses) * 100 if total_responses else 0

    chart_data = {
        'labels': ['Accuracy (%)', 'Avg Latency (ms)', 'Total Responses'],
        'values': [accuracy, avg_latency, total_responses],
        'accuracy': accuracy,
        'avg_latency': avg_latency,
        'total_responses': total_responses
    }
    return render(request, 'basic/test_statistics.html', {'test_id': test_id, 'chart_data': chart_data})

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
    test_sessions = TestSession.objects.all()
    return render(request, "basic/testresults.html", {"test_sessions": test_sessions})
