from django.shortcuts import render,redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models

from basic.models import TestSession,User, Response


# Create your views here.


def login_view(request):
    return render(request,'basic/login.html')

def test_page(request):
    return render(request, 'basic/take_test.html')


def user_login(request):
    if request.method == "POST":
        # Getting the username and password in the form post in the html page/
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Authentication is successfull
            login(request, user)
            return redirect("basic:dashboard")  # Redirecting to the dashboard
        else:
            # Authentication is denied
            messages.error(request, "Invalid username or password")
            return  redirect("basic:login") # Redirecting to the login page, when refreshed

    return render(request, "basic/login.html")


@login_required(login_url='/basic/')
def dashboard(request):
    return render(request, 'basic/dashboard.html')

def results(request):
    test_sessions = TestSession.objects.filter(doctor=request.user)
    return render(request, 'basic/results.html', {'test_sessions': test_sessions})

def statistics(request):
    return render(request, 'basic/statistics.html')

def newtest(request):
    return render(request, "basic/newtest.html")

def base(request):
    return render(request, "basic/base.html")

def landing(request):
     total_tests = TestSession.objects.count()  # Count all test sessions
     total_doctors = User.objects.filter(testsession__isnull=False).distinct().count()  # Count unique doctors with tests

     return render(request, "basic/landing.html", {
        "total_tests": total_tests,
        "total_doctors": total_doctors,
    })
def logout_view(request):
    logout(request)  
    return redirect('basic:landing') 



