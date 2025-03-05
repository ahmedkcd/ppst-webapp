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

# Create test sessions
test_sessions = [
    TestSession.objects.create(doctor=doctors[0], age=35, date=timezone.now(), duration=timedelta(minutes=30)),
    TestSession.objects.create(doctor=doctors[1], age=40, date=timezone.now(), duration=timedelta(hours=1)),
]

print(f"Created test sessions: {[session.test_id for session in test_sessions]}")

# Create stimuli data
stimuli_data = [
    ("4231", "1234", 4, "Numeric"), ("5892", "2589", 4, "Numeric"), ("7613", "1367", 4, "Numeric"),
    ("19845", "14589", 5, "Numeric"), ("37260", "02367", 5, "Numeric"), ("90431", "01349", 5, "Numeric"),
    ("A1B2", "12AB", 4, "AlphaNumeric"), ("M4X7", "47MX", 4, "AlphaNumeric"), ("C9D3", "39CD", 4, "AlphaNumeric"),
    ("K7L2M", "27KLM", 5, "AlphaNumeric"), ("Z8Y4X", "48XYZ", 5, "AlphaNumeric"), ("P5Q1R", "15PQR", 5, "AlphaNumeric"),
]

stimuli = [
    Stimuli.objects.create(stimulus=s[0], correct_response=s[1], span=s[2], type=s[3])
    for s in stimuli_data
]

print(f"Created stimuli: {[stim.stim_id for stim in stimuli]}")

# Create responses for a fully completed test session with some incorrect answers
responses = [
    Response.objects.create(test=test_sessions[0], stim=stimuli[0], response="1234", latency=2.1, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[1], response="5893", latency=2.5, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[2], response="1367", latency=2.0, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[3], response="14859", latency=2.3, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[4], response="02367", latency=2.8, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[5], response="90341", latency=1.9, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[6], response="12AB", latency=2.2, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[7], response="4MX8", latency=2.7, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[8], response="39CD", latency=1.8, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[9], response="27KLM", latency=2.4, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[10], response="4X8YY", latency=3.0, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[11], response="15PQR", latency=2.6, is_correct=True),
]

print(f"Created responses: {[resp.response_id for resp in responses]}")

# Verify queries
tasks = TestSession.objects.filter(doctor=doctors[0])
print(f"Tests assigned to Dr. Smith: {[t.test_id for t in tasks]}")

responses = Response.objects.filter(test=test_sessions[0])
print(f"Responses for Test {test_sessions[0].test_id}: {[r.response for r in responses]}")

print("✅ Database populated successfully!")
