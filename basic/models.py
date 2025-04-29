from django.contrib.auth.models import User  # Use built-in User model
from django.db import models
from django.db.models import Avg


# TestSession now references User instead of Doctor
class TestSession(models.Model):
    test_id = models.TextField(primary_key=True)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to built-in User model
    age = models.IntegerField()
    date = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True)
    avg_latency = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    stimuli_order = models.TextField(null=True)
    state = models.TextField(default="incomplete")
    language = models.TextField(default="en")

    def __str__(self):
        return f"Test {self.test_id} - Age {self.age} with Dr. {self.doctor.username}"


# Stimuli model to store stimulus data used in test sessions
class Stimuli(models.Model):
    stim_id = models.AutoField(primary_key=True)
    stimulus = models.TextField()
    correct_response = models.TextField()
    span = models.IntegerField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return f"Stimulus {self.stim_id} ({self.type})"


# Response Model which stores each patient’s response and its attributes for a given test
class Response(models.Model):
    response_id = models.AutoField(primary_key=True)
    test = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    stim = models.ForeignKey(Stimuli, on_delete=models.CASCADE)
    response = models.TextField(null=True)
    latencies = models.TextField(null=True)
    avg_latency = models.FloatField(null=True)
    is_correct = models.BooleanField(null=True)

    def __str__(self):
        return f"Response {self.response_id} (Test {self.test.test_id})"


class Statistics(models.Model):
    stats_id = models.AutoField(primary_key=True)
    total_tests = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    avg_latency = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update_statistics(self):
        """
        Updates the statistics based on TestSession and Response data.
        """
        self.total_tests = TestSession.objects.count()
        self.total_responses = Response.objects.count()
        self.avg_latency = Response.objects.aggregate(avg_latency=Avg('latency'))['avg_latency']
        self.accuracy = Response.objects.aggregate(avg_accuracy=Avg('is_correct'))['avg_accuracy']
        self.save()

    def __str__(self):
        return f"Site-wide Stats - {self.total_tests} Tests, {self.total_responses} Responses"

    @classmethod
    def refresh_statistics(cls):
        """
        Refreshes the statistics record.
        Ensures only one instance of Statistics exists.
        """
        stats, _ = cls.objects.get_or_create(pk=1)
        stats.update_statistics()
