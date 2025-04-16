from django.contrib import admin
from .models import TestSession, Stimuli, Response

# ✅ Customize the admin panel for Response model
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    # Columns to display in the admin list view
    list_display = ("response_id", "test", "stim", "response", "is_correct", "created_at")
    
    # Enable search bar on response text
    search_fields = ("response",)

    # Add filters in the right sidebar
    list_filter = ("is_correct", "created_at")


# ✅ Customize the admin panel for Stimuli model
@admin.register(Stimuli)
class StimuliAdmin(admin.ModelAdmin):
    # Show stimulus details in admin
    list_display = ("stim_id", "stimulus", "type", "span", "created_at")


# ✅ Customize the admin panel for TestSession model
@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    # Show test session details for doctors/admin
    list_display = ("test_id", "doctor", "status", "accuracy", "avg_latency", "date", "created_at")

    # Filter by test status and language
    list_filter = ("status", "language")
