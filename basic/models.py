import uuid  # ✅ import uuid for generating unique IDs
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class TestSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    test_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ changed from AutoField to UUIDField
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    date = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    avg_latency = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    stimuli_order = models.TextField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    language = models.CharField(max_length=10, default="en")

    def __str__(self):
        return f"Test {self.test_id} (Age: {self.age}) - Dr. {self.doctor.username}"


class Stimuli(models.Model):
    stim_id = models.AutoField(primary_key=True)
    stimulus = models.TextField()
    correct_response = models.TextField()
    span = models.IntegerField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return f"Stimulus {self.stim_id} [{self.type}]"


class Response(models.Model):
    response_id = models.AutoField(primary_key=True)
    test = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    stim = models.ForeignKey(Stimuli, on_delete=models.CASCADE)
    response = models.TextField(null=True)
    latencies = models.TextField(null=True)
    is_correct = models.BooleanField(null=True)

    def __str__(self):
        return f"Response {self.response_id} for Test {self.test.test_id}"


class Statistics(models.Model):
    stats_id = models.AutoField(primary_key=True)
    total_tests = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    avg_latency = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update_statistics(self):
        self.total_tests = TestSession.objects.count()
        self.total_responses = Response.objects.count()
        self.avg_latency = Response.objects.aggregate(avg_latency=Avg('latencies'))['avg_latency']
        self.accuracy = Response.objects.aggregate(avg_accuracy=Avg('is_correct'))['avg_accuracy']
        self.save()

    @classmethod
    def refresh_statistics(cls):
        stats, _ = cls.objects.get_or_create(pk=1)
        stats.update_statistics()

    def __str__(self):
        return f"Stats: {self.total_tests} Tests, {self.total_responses} Responses"
