from django.shortcuts import render
from .models import Notification

# Create your views here.
def listnotifications(request, username):
    notifications = Notification.objects.filter(users__username=username)

    return render(request, "notifications/listnotifications.html", {
                'username': username,
                'notifications': notifications,
    })
