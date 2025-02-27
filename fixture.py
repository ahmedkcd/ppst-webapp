from django.contrib.auth.models import User
from basic.models import TestSession, Stimuli, Response, Statistics
from django.utils import timezone

# Delete existing objects
for model in [TestSession, Stimuli, Response, Statistics]:
    model.objects.all().delete()

# Create users (doctors)
doctors = [
    User.objects.create_user(username="dr_smith", email="drsmith@example.com", password="securepassword"),
    User.objects.create_user(username="dr_jones", email="drjones@example.com", password="securepassword"),
]
for doctor in doctors:
    doctor.is_staff = True  # Allow access to Django admin
    doctor.save()

# Create test sessions
test_sessions = [
    TestSession.objects.create(doctor=doctors[0], age=35, date=timezone.now(), duration="00:30:00"),
    TestSession.objects.create(doctor=doctors[1], age=40, date=timezone.now(), duration="01:00:00"),
]

# Create stimuli
stimuli = [
    Stimuli.objects.create(stimulus="Red Circle", correct_response="Press Red Button", span=3, type="Visual"),
    Stimuli.objects.create(stimulus="Beep Sound", correct_response="Press Any Key", span=2, type="Auditory"),
]

# Create responses
responses = [
    Response.objects.create(test=test_sessions[0], stim=stimuli[0], response="Pressed Red Button", latency=2.5, is_correct=True),
    Response.objects.create(test=test_sessions[1], stim=stimuli[1], response="Pressed Any Key", latency=1.8, is_correct=True),
]

# Create statistics
Statistics.objects.create(avg_latency=2.15, accuracy=90.0, total_tests=2, total_responses=2)

# Print useful queries
tasks = TestSession.objects.filter(doctor=doctors[0])
print(f"Tests assigned to Dr. Smith: {[t.test_id for t in tasks]}")

responses = Response.objects.filter(test=test_sessions[0])
print(f"Responses for Test {test_sessions[0].test_id}: {[r.response for r in responses]}")

print("Database populated successfully!")
