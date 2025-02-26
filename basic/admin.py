from django.contrib import admin

from .models import TestSession, Stimuli, Response, Statistics


# Register your models here.
admin.site.register(TestSession)
admin.site.register(Stimuli)
admin.site.register(Response)
admin.site.register(Statistics)