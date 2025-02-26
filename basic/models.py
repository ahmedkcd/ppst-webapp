from django.db import models
from django.contrib.auth.models import User  # Use built-in User model

# TestSession now references User instead of Doctor
class TestSession(models.Model):
    test_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to built-in User model
    age = models.IntegerField()
    date = models.DateTimeField()
    duration = models.DurationField()

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
    response = models.TextField()
    latency = models.FloatField()
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Response {self.response_id} (Test {self.test.test_id})"


# Model for storing statistical data
class Statistics(models.Model):
    stats_id = models.AutoField(primary_key=True)
    avg_latency = models.FloatField()
    accuracy = models.FloatField()
    total_tests = models.IntegerField()
    total_responses = models.IntegerField()

    def __str__(self):
        return f"Aggregate Stats - {self.total_tests} Tests, {self.total_responses} Responses"
