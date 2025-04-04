from django.contrib import admin
from .models import TestSession, Stimuli, Response
from .forms import TestSessionForm

class TestSessionAdmin(admin.ModelAdmin):
    form = TestSessionForm

admin.site.register(TestSession, TestSessionAdmin)
admin.site.register(Stimuli)
admin.site.register(Response)
