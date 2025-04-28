import os

import django
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
        user.set_password("securepassword")
        user.is_staff = False  # admin access
        user.save()
    return user

doctors = [
    get_or_create_user("dr_smith", "drsmith@example.com"),
    get_or_create_user("dr_jones", "drjones@example.com"),
    get_or_create_user("dr_matt", "drmatt@example.com"),
    get_or_create_user("dr_atilla", "dratilla@example.com"),
    get_or_create_user("dr_tuch", "drtuch@example.com"),
    get_or_create_user("dr_rossi", "drrossi@example.com"),
]

print(f"Doctors in database: {[doctor.username for doctor in doctors]}")

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

import random
import uuid
from random import randrange
from datetime import timedelta, datetime
from django.utils import timezone


def random_date(): # https://stackoverflow.com/questions/553303/how-to-generate-a-random-date-between-two-other-dates
    """
    This function will return a random datetime between two datetime
    objects.
    """
    d1 = datetime.strptime('1/1/2023 1:30 PM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.strptime('1/1/2024 4:50 AM', '%m/%d/%Y %I:%M %p')
    d1 = timezone.make_aware(d1)
    d2 = timezone.make_aware(d2)
    delta = d2 - d1
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return d1 + timedelta(seconds=random_second)


test_sessions = []
all_stimuli = Stimuli.objects.exclude(type="Practice")
test_orders = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8],
        [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]
languages = ["en", "sp"]


for i in range(100):
    doctor = doctors[i % len(doctors)]
    age = random.randint(30, 90)
    duration = timedelta(minutes=random.randint(20, 60))
    date = random_date()
    test_uuid = str(uuid.uuid4())
    language = random.choice(languages)

    selected_order = random.choice(test_orders)
    stimuli_list = list(all_stimuli)
    ordered_stimuli = [stimuli_list[i] for i in selected_order]
    stimuli_order_str = ",".join(map(str, selected_order))


    session = TestSession.objects.create(
        doctor=doctor,
        age=age,
        date=date,
        duration=duration,
        test_id=test_uuid,
        stimuli_order=stimuli_order_str,
        language=language
    )
    test_sessions.append(session)

    correct_count = 0
    total_latency = 0
    latency_count = 0

    # Create responses for each stimulus
    for stim in ordered_stimuli:
        # Random chance of being correct
        is_correct = random.choice([True, False])
        if is_correct:
            response_text = stim.correct_response
        else:
            # Generate a wrong response of same length
            chars = '12345679BHGFMRXY'
            response_text = ''.join(random.choices(chars, k=len(stim.correct_response)))
            # make sure it's not accidentally correct
            if response_text == stim.correct_response:
                response_text = ''.join(random.choices(chars, k=len(stim.correct_response)))

        latencies = [round(random.uniform(100, 5000)) for _ in range(len(stim.correct_response))]
        latencies_str = ",".join(map(str, latencies))  # Convert latencies to comma-separated string

        Response.objects.create(
            test=session,
            stim=stim,
            response=response_text,
            latencies=latencies_str,
            is_correct=is_correct
        )

        if is_correct:
            correct_count += 1
        total_latency += sum(latencies)
        latency_count += len(latencies)

    if latency_count > 0:
        session.avg_latency = total_latency / latency_count
    if latency_count > 0:  # same as total responses
        session.accuracy = correct_count / latency_count
    session.save()

print(f" Created {len(test_sessions)} test sessions with responses.")


# Verify queries
tasks = TestSession.objects.filter(doctor=doctors[0])
print(f"Tests assigned to Dr. Smith: {[t.test_id for t in tasks]}")

responses = Response.objects.filter(test=test_sessions[0])
print(f"Responses for Test {test_sessions[0].test_id}: {[r.response for r in responses]}")

print(" Database populated successfully!")
