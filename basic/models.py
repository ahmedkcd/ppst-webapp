# 🌐 Standard library imports
import uuid  # For unique identifiers on TestSessions
import json  # To safely parse JSON from stored latencies

# 📦 Django imports
from django.contrib.auth.models import User  # Reusing Django's built-in user model
from django.db import models  # Core Django ORM
from django.db.models import Avg  # For calculating averages
from django.utils import timezone  # For date/time tracking

# 🔄 Signal handling for automatic updates
from django.db.models.signals import post_save
from django.dispatch import receiver


# 🧪 TestSession — Represents a single test given to a patient
class TestSession(models.Model):
    # Choices for the status of the test
    STATUS_CHOICES = [
        ('pending', 'Pending'),     # Created but not yet started
        ('active', 'Active'),       # In progress
        ('completed', 'Completed'), # Finished
    ]

    test_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique ID for each test
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)  # Linked to a doctor (user)
    age = models.IntegerField()  # Age of the patient
    date = models.DateTimeField(null=True)  # When the test was conducted
    duration = models.DurationField(null=True)  # Total duration of the test
    avg_latency = models.FloatField(null=True)  # Calculated average latency in seconds
    accuracy = models.FloatField(null=True)  # Accuracy in percentage (e.g., 87.5)
    stimuli_order = models.TextField(null=True)  # Order of stimuli presented (as a comma-separated string)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Test status
    language = models.CharField(max_length=10, default="en")  # Language used during the test
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the test session was created

    def __str__(self):
        return f"Test {self.test_id} (Age: {self.age}) - Dr. {self.doctor.username}"

    # 📊 Calculate and save the average latency and accuracy from related responses
    def calculate_statistics(self):
        responses = self.response_set.all()  # All responses for this test
        total = responses.count()  # Total responses
        correct = responses.filter(is_correct=True).count()  # Number of correct responses

        # Extract first latency value from each response, handling JSON safely
        latency_values = []
        for r in responses:
            try:
                latency_list = r.latencies if isinstance(r.latencies, list) else json.loads(r.latencies)
                latency_values.append(float(latency_list[0]))  # Use only the first latency
            except Exception:
                continue  # Ignore malformed data

        # Calculate average if we have latency data
        avg_latency = sum(latency_values) / len(latency_values) if latency_values else 0

        self.accuracy = (correct / total) * 100 if total else 0  # Avoid divide by zero
        self.avg_latency = round(avg_latency, 2)
        self.status = 'completed'  # Mark test as completed after processing
        self.save()  # Save updated fields


# 🔡 Stimuli — A stimulus presented to the user during a test
class Stimuli(models.Model):
    stim_id = models.AutoField(primary_key=True)  # Auto-increment ID
    stimulus = models.TextField()  # Stimulus content (e.g., numbers/letters)
    correct_response = models.TextField()  # The correct response expected from the patient
    span = models.IntegerField()  # Number of characters/digits in the stimulus
    type = models.CharField(max_length=100)  # Type: Numeric, AlphaNumeric, Practice
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation

    def __str__(self):
        return f"Stimulus {self.stim_id} [{self.type}]"


# ✅ Response — Stores a patient's response to a specific stimulus during a test
class Response(models.Model):
    response_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    test = models.ForeignKey(TestSession, on_delete=models.CASCADE)  # Linked test session
    stim = models.ForeignKey(Stimuli, on_delete=models.CASCADE)  # Stimulus for this response
    response = models.TextField(null=True, blank=True)  # User's response (nullable)
    latencies = models.JSONField(null=True, blank=True)  # Response times (list of floats)
    is_correct = models.BooleanField(null=True)  # Whether the response was correct
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when saved

    def __str__(self):
        return f"Response {self.response_id} for Test {self.test.test_id}"


# 📊 Statistics — Aggregated stats across all test sessions in the system
class Statistics(models.Model):
    stats_id = models.AutoField(primary_key=True)  # ID for this record
    total_tests = models.IntegerField(default=0)  # Total number of tests ever run
    total_responses = models.IntegerField(default=0)  # Total number of responses across all tests
    avg_latency = models.FloatField(null=True, blank=True)  # Global average latency
    accuracy = models.FloatField(null=True, blank=True)  # Global accuracy (%)
    last_updated = models.DateTimeField(auto_now=True)  # Auto-updated on every save

    # 🔄 Recalculate all system-wide stats
    def update_statistics(self):
        self.total_tests = TestSession.objects.count()
        self.total_responses = Response.objects.count()

        # Calculate average latency from all responses
        all_latencies = []
        for r in Response.objects.all():
            try:
                latency_list = r.latencies if isinstance(r.latencies, list) else json.loads(r.latencies)
                all_latencies.append(float(latency_list[0]))
            except Exception:
                continue  # Skip if invalid

        self.avg_latency = round(sum(all_latencies) / len(all_latencies), 2) if all_latencies else 0
        self.accuracy = (Response.objects.aggregate(avg_accuracy=Avg('is_correct'))['avg_accuracy'] or 0) * 100
        self.save()

    # Helper: creates or updates the statistics record
    @classmethod
    def refresh_statistics(cls):
        stats, _ = cls.objects.get_or_create(pk=1)
        stats.update_statistics()

    def __str__(self):
        return f"Stats: {self.total_tests} Tests, {self.total_responses} Responses"


# 📢 Signal receiver: auto-refresh stats when a TestSession is completed
@receiver(post_save, sender=TestSession)
def update_statistics_on_test_complete(sender, instance, **kwargs):
    if instance.status == 'completed':
        Statistics.refresh_statistics()
