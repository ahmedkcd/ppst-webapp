import json
import csv
import uuid
import random
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import models, transaction
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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
def doctor_dashboard(request):
    doctor = request.user
    total_tests = TestSession.objects.filter(doctor=doctor).count()
    active_tests = TestSession.objects.filter(doctor=doctor, status="active").count()
    pending_tests = TestSession.objects.filter(doctor=doctor, status="pending").count()
    recent_tests = TestSession.objects.filter(
        doctor=doctor, accuracy__isnull=False
    ).order_by("-date")[:10]
    labels = [test.date.strftime("%b %d") for test in recent_tests]
    scores = [round(test.accuracy, 2) for test in recent_tests]
    return render(request, 'basic/doctor_dashboard.html', {
        "user": doctor,
        "total_tests": total_tests,
        "active_tests": active_tests,
        "pending_tests": pending_tests,
        "recent_tests": recent_tests,
        "labels": json.dumps(labels),
        "scores": json.dumps(scores),
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
        response = Response.objects.create(test=test_session, stim=stimulus)
        responses.append({"response_id": response.response_id, "stimulus": stimulus.stim_id})
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
                test_session = None
                for response_entry in responses_data:
                    response_id = response_entry.get("response_id")
                    user_response = response_entry.get("response")
                    latency = response_entry.get("latency")
                    is_correct = response_entry.get("is_correct")
                    response = get_object_or_404(Response, response_id=response_id)
                    response.response = user_response
                    response.latencies = latency
                    response.is_correct = is_correct
                    response.save()
                    test_session = response.test
                if test_session:
                    stats = test_session.response_set.aggregate(
                        avg_latency=models.Avg("latencies"),
                        total_responses=models.Count("response_id"),
                        correct_responses=models.Count("response_id", filter=models.Q(is_correct=True))
                    )
                    test_session.avg_latency = stats["avg_latency"]
                    test_session.accuracy = (
                        (stats["correct_responses"] / stats["total_responses"]) * 100
                        if stats["total_responses"] else 0
                    )
                    test_session.status = "completed"
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
    avg_latency = responses.aggregate(models.Avg('latencies'))['latencies__avg'] or 0
    accuracy = (correct_responses / total_responses) * 100 if total_responses else 0
    chart_data = {
        'labels': ['Accuracy (%)', 'Avg Latency (ms)', 'Total Responses'],
        'values': [accuracy, avg_latency, total_responses]
    }
    return render(request, 'basic/test_statistics.html', {'test_id': test_id, 'chart_data': chart_data})

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
    test = get_object_or_404(TestSession, test_id=uuid.UUID(test_id))
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
