<<<<<<< HEAD
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
=======
from basic.models import Computed
from django.contrib.auth.models import User
from tasks.models import Project, Member, Notification, Task
from django.utils import timezone

# Delete existing objects
for c in [Computed, Project, Member, Notification, Task]:
    c.objects.all().delete()


# Install fixture
newobject = Computed(input=80,output=6400,time_computed=timezone.now())
newobject.save()

projects = [Project.objects.create(name=name) for name in ["Wireframes", "Models", "Fake data"]]
for project in projects:
    project.save()

members = [Member.objects.create_user(username= "m"+str(i)) for i in range(0,10)]
for m in members:
    m.save()


# Task status 0 = not started, 1 = in progress, 2 = completed
t0 = Task(description="Home page", project=projects[0], assignee=members[0])
t0.save()
t1 = Task(description="Login page", project=projects[0], assignee=members[1])
t1.save()
t2 = Task(description="Tasks dashboard page", project=projects[0], assignee=members[1])
t2.started()
t2.save()

t3 = Task(description="Member model", project=projects[1], assignee=members[2])
t3.started()
t3.save()
t4 = Task(description="Task model", project=projects[1], assignee=members[4])
t4.completed()
t4.save()
t5 = Task(description="Notification model", project=projects[1], assignee=members[3])
t5.save()
t6 = Task(description="Project model", project=projects[1], assignee=members[1])
t6.started()
t6.save()

t7 = Task(description="Fake members", project=projects[2], assignee=members[4])
t7.completed()
t7.save()
t8 = Task(description="Fake notifications", project=projects[2], assignee=members[5])
t8.started()
t8.save()
t9 = Task(description="Fake projects", project=projects[2], assignee=members[5])
t9.started()
t9.save()
t10 = Task(description="Fake tasks", project=projects[2], assignee=members[1])
t10.save()



n1 = Notification(message="Your wireframe task is running behind schedule!")
n1.save()
n1.users.add(members[0], members[1])

n2 = Notification(message="Good job with your progress on Task model")
n2.save()
n2.users.add(members[4])

n3 = Notification(message="Terrific job on your previous project!")
n3.save()
n3.users.add(members[1])


# Some useful queries that may be pertinent while writing view functions

# All tasks within project Models

tasks = Task.objects.filter(project__name="Models")
print(f"Tasks within the project Models are: {[t.description for t in tasks]}")

# Members working on project Fake data

members=Task.objects.filter(project__name="Fake data").values('assignee').distinct()
print(f"\nTeam members working on project Fake data are: \
{[Member.objects.get(pk=x['assignee']).username for x in members]}")

# Tasks assigned to member m4

tasks = Task.objects.filter(assignee__username="m4")
print("\nTasks assigned to user m4 are: {[t.description for t in tasks]}")

# Notifications for member m1

notifications = Member.objects.filter(username="m1")[0].notification_set.all()
print(f"\nNotifications for team member m1 are: {[n.message for n in notifications]}")

# Task description for those tasks have yet to be started within project Wireframes

descriptions = Task.objects.filter(project__name="Wireframes", status = 0).values_list('description', flat=True)
print(f"\nTasks that have yet to start in project Wireframes: {list(descriptions)}")

>>>>>>> djangostarter/Amyr-Final-Prog-Branch
