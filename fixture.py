import django
import os
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from basic.models import TestSession, Stimuli, Response

# Setup Django environment (useful if running outside `manage.py shell`)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoproject.settings")
django.setup()

# Delete existing objects to start fresh (except users)
for model in [TestSession, Stimuli, Response]:
    model.objects.all().delete()

print("Existing data cleared.")

# Ensure unique users
def get_or_create_user(username, email):
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    if created:
        user.set_password("securepassword")  # Set a password if newly created
        user.is_staff = False  # admin access
        user.save()
    return user

# Create or retrieve sample doctors
doctors = [
    get_or_create_user("dr_smith", "drsmith@example.com"),
    get_or_create_user("dr_jones", "drjones@example.com"),
]

print(f"Doctors in database: {[doctor.username for doctor in doctors]}")

# Create test sessions with correct timedelta format
test_sessions = [
    TestSession.objects.create(doctor=doctors[0], age=35, date=timezone.now(), duration=timedelta(minutes=30)),
    TestSession.objects.create(doctor=doctors[1], age=40, date=timezone.now(), duration=timedelta(hours=1)),
]

print(f"Created test sessions: {[session.test_id for session in test_sessions]}")

# Create stimuli
stimuli = [
    Stimuli.objects.create(stimulus="42316", correct_response="12346", span=5, type="Numeric"),
    Stimuli.objects.create(stimulus="219CZG", correct_response="123CGZ", span=6, type="AlphaNumeric"),
]

print(f"Created stimuli: {[stim.stim_id for stim in stimuli]}")

# Create responses
responses = [
    Response.objects.create(test=test_sessions[0], stim=stimuli[0], response="12346", latency=2.5, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[1], response="321CDX", latency=1.8, is_correct=False),
]

print(f"Created responses: {[resp.response_id for resp in responses]}")

# Verify queries
tasks = TestSession.objects.filter(doctor=doctors[0])
print(f"Tests assigned to Dr. Smith: {[t.test_id for t in tasks]}")

responses = Response.objects.filter(test=test_sessions[0])
print(f"Responses for Test {test_sessions[0].test_id}: {[r.response for r in responses]}")

print("✅ Database populated successfully!")
