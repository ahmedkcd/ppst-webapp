from django.contrib import admin

from .models import Doctor, TestSession, Stimuli, Response, Statistics, Computed


# Register your models here.
admin.site.register(Doctor)
admin.site.register(TestSession)
admin.site.register(Stimuli)
admin.site.register(Response)
admin.site.register(Statistics)
admin.site.register(Computed)