import os
import random
from datetime import timedelta

# ✅ Set Django settings before importing anything Django-specific
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "basic.settings")
import django
django.setup()

# ✅ Django imports after setup
from django.contrib.auth.models import User
from django.utils import timezone
from basic.models import TestSession, Stimuli, Response

# 🧹 Delete existing test-related data (except users)
for model in [TestSession, Stimuli, Response]:
    model.objects.all().delete()
print("🧼 Existing test data cleared.")


# 👩‍⚕️ Ensure doctors exist
def get_or_create_user(username, email):
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    if created:
        user.set_password("securepassword")
        user.is_staff = False
        user.save()
    return user

doctors = [
    get_or_create_user("dr_smith", "drsmith@example.com"),
    get_or_create_user("dr_jones", "drjones@example.com"),
]
print(f"👩‍⚕️ Doctors available: {[doctor.username for doctor in doctors]}")


# 🧪 Create test sessions (UUIDs auto-assigned, so we do NOT set test_id manually)
test_sessions = []
for i in range(4):
    session = TestSession.objects.create(
        doctor=doctors[i % 2],
        age=30 + i,
        date=timezone.now() - timedelta(days=i),
        duration=timedelta(minutes=25 + i * 5),
        status="completed"
    )
    test_sessions.append(session)

print(f"🧾 Created test sessions: {[str(session.test_id) for session in test_sessions]}")


# 🎯 Manually defined stimuli
stimuli_data = [
    ("7613", "1367", 4, "Numeric"),
    ("4231", "1234", 4, "Numeric"),
    ("5279", "2579", 4, "Numeric"),
    ("19457", "14579", 5, "Numeric"),
    ("36279", "23679", 5, "Numeric"),
    ("91347", "13479", 5, "Numeric"),
    ("B1H3", "13BH", 4, "AlphaNumeric"),
    ("M4X7", "47MX", 4, "AlphaNumeric"),
    ("G9R2", "29GR", 4, "AlphaNumeric"),
    ("RH12M", "12HMR", 5, "AlphaNumeric"),
    ("B9Y4X", "49BXY", 5, "AlphaNumeric"),
    ("F5M1R", "15FMR", 5, "AlphaNumeric"),
]

# 💾 Create stimuli in DB
stimuli = [
    Stimuli.objects.create(stimulus=s[0], correct_response=s[1], span=s[2], type=s[3])
    for s in stimuli_data
]
print(f"📚 Created {len(stimuli)} stimuli.")


# 📝 Create randomized responses
responses = []
for test in test_sessions:
    for stim in stimuli:
        is_correct = random.choices([True, False], weights=[0.7, 0.3])[0]
        if is_correct:
            user_response = stim.correct_response
        else:
            scrambled = list(stim.correct_response)
            random.shuffle(scrambled)
            user_response = ''.join(scrambled)
            if user_response == stim.correct_response:
                user_response += "X"

        latency = round(random.uniform(1.5, 3.5), 2)

        response = Response.objects.create(
            test=test,
            stim=stim,
            response=user_response,
            latencies=[latency],
            is_correct=is_correct
        )

        responses.append(response)

    # 📊 Update statistics on the session after creating all responses
    test.calculate_statistics()
    print(f"📊 Test {str(test.test_id)} — Accuracy: {test.accuracy:.2f}%, Avg Latency: {test.avg_latency:.2f}s")


# ✅ Final success message
print(f"✅ Total responses created: {len(responses)}")
print("🎉 Fixture loaded successfully!")
