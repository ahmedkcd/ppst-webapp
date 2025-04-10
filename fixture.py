import os
from datetime import timedelta

import django
from django.contrib.auth.models import User
from django.utils import timezone

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
        user.set_password("securepassword")
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
    TestSession.objects.create(doctor=doctors[0], age=35, date=timezone.now(), duration=timedelta(minutes=30),
                               test_id=1),
    TestSession.objects.create(doctor=doctors[1], age=40, date=timezone.now(), duration=timedelta(hours=1), test_id=2),
    TestSession.objects.create(doctor=doctors[0], age=47, date=timezone.now(), duration=timedelta(hours=1), test_id=3),
    TestSession.objects.create(doctor=doctors[1], age=38, date=timezone.now(), duration=timedelta(minutes=30),
                               test_id=4),
]

print(f"Created test sessions: {[session.test_id for session in test_sessions]}")

# Create stimuli data
stimuli_data = [
    # Numeric (4-span)
    ("7613", "1367", 4, "Numeric"),
    ("4231", "1234", 4, "Numeric"),
    ("5279", "2579", 4, "Numeric"),

    # Numeric (5-span)
    ("19457", "14579", 5, "Numeric"),
    ("36279", "23679", 5, "Numeric"),
    ("91347", "13479", 5, "Numeric"),

    # Alphanumeric (4-span)
    ("B1H3", "13BH", 4, "AlphaNumeric"),
    ("M4X7", "47MX", 4, "AlphaNumeric"),
    ("G9R2", "29GR", 4, "AlphaNumeric"),

    # Alphanumeric (5-span)
    ("RH12M", "12HMR", 5, "AlphaNumeric"),
    ("B9Y4X", "49BXY", 5, "AlphaNumeric"),
    ("F5M1R", "15FMR", 5, "AlphaNumeric"),

    # Practice (mixed examples)
    ("B129", "129B", 4, "Practice"),
    ("HG97", "79GH", 4, "Practice"),
]

stimuli = [
    Stimuli.objects.create(stimulus=s[0], correct_response=s[1], span=s[2], type=s[3])
    for s in stimuli_data
]

print(f"Created stimuli: {[stim.stim_id for stim in stimuli]}")

# Create responses for a fully completed test session with some incorrect answers
responses = [
    # Test Session 1
    Response.objects.create(test=test_sessions[0], stim=stimuli[0], response="1234", latencies=2.1, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[1], response="5893", latencies=2.5, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[2], response="1367", latencies=2.0, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[3], response="14859", latencies=2.3, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[4], response="02367", latencies=2.8, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[5], response="90341", latencies=1.9, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[6], response="12AB", latencies=2.2, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[7], response="4MX8", latencies=2.7, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[8], response="39CD", latencies=1.8, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[9], response="27KLM", latencies=2.4, is_correct=True),
    Response.objects.create(test=test_sessions[0], stim=stimuli[10], response="4X8YY", latencies=3.0, is_correct=False),
    Response.objects.create(test=test_sessions[0], stim=stimuli[11], response="15PQR", latencies=2.6, is_correct=True),
    # Test Session 2
    Response.objects.create(test=test_sessions[1], stim=stimuli[0], response="1234", latencies=2.2, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[1], response="2589", latencies=2.6, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[2], response="1367", latencies=2.4, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[3], response="14859", latencies=3.1, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[4], response="02367", latencies=2.7, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[5], response="01349", latencies=2.9, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[6], response="12AB", latencies=2.3, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[7], response="47MX", latencies=2.8, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[8], response="39CD", latencies=3.0, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[9], response="27KLM", latencies=3.2, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[10], response="48XYZ", latencies=2.5, is_correct=False),
    Response.objects.create(test=test_sessions[1], stim=stimuli[11], response="15PQR", latencies=2.6, is_correct=True),
    # Test Session 3
    Response.objects.create(test=test_sessions[2], stim=stimuli[0], response="1234", latencies=2.1, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[1], response="2589", latencies=2.4, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[2], response="1367", latencies=2.3, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[3], response="14589", latencies=3.0, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[4], response="02367", latencies=2.6, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[5], response="01349", latencies=2.7, is_correct=False),
    Response.objects.create(test=test_sessions[2], stim=stimuli[6], response="12AB", latencies=2.2, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[7], response="47MX", latencies=2.5, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[8], response="39CD", latencies=2.9, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[9], response="27KLM", latencies=3.1, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[10], response="48XYZ", latencies=3.2, is_correct=True),
    Response.objects.create(test=test_sessions[2], stim=stimuli[11], response="15PQR", latencies=2.6, is_correct=False),
    # Test Session 4
    Response.objects.create(test=test_sessions[3], stim=stimuli[0], response="1234", latencies=2.0, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[1], response="2589", latencies=2.5, is_correct=False),
    Response.objects.create(test=test_sessions[3], stim=stimuli[2], response="1367", latencies=2.6, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[3], response="14859", latencies=2.8, is_correct=False),
    Response.objects.create(test=test_sessions[3], stim=stimuli[4], response="02367", latencies=3.0, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[5], response="01349", latencies=2.9, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[6], response="12AB", latencies=2.3, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[7], response="47MX", latencies=2.4, is_correct=False),
    Response.objects.create(test=test_sessions[3], stim=stimuli[8], response="39CD", latencies=2.6, is_correct=False),
    Response.objects.create(test=test_sessions[3], stim=stimuli[9], response="27KLM", latencies=2.7, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[10], response="48XYZ", latencies=2.8, is_correct=True),
    Response.objects.create(test=test_sessions[3], stim=stimuli[11], response="15PQR", latencies=3.1, is_correct=True),
]

print(f"Created responses: {[resp.response_id for resp in responses]}")

# Verify queries
tasks = TestSession.objects.filter(doctor=doctors[0])
print(f"Tests assigned to Dr. Smith: {[t.test_id for t in tasks]}")

responses = Response.objects.filter(test=test_sessions[0])
print(f"Responses for Test {test_sessions[0].test_id}: {[r.response for r in responses]}")

print("✅ Database populated successfully!")
