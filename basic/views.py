from django.shortcuts import render,redirect
from django.http import Http404
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.


def login_view(request):
    return render(request,'basic/login.html')

@login_required
def dashboard(request):
    return render(request,'basic/dashboard.html')


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
            return  redirect("basic:login") # Redirecting to the login

    return render(request, "basic/login.html")





