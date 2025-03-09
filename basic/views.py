<<<<<<< HEAD
# Create your views here.

# stimulus are hard coded

# pseudo ///
# first generate a new test model with user id and age
# then generate a response model for every stimulus
# link each response with a unique stimulus and that same test id

import json
import random

from django.db import models
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Response
from .models import TestSession, Stimuli


def generate_test(request):
    age = request.GET.get("age", None)  # Default to None if not provided
    if age is None:
        return JsonResponse({"error": "Age parameter is required."}, status=400)

    test_session = TestSession.objects.create(
        doctor=request.user,
        age=age,
    )

    stimuli_list = list(Stimuli.objects.all())
    random.shuffle(stimuli_list)

    responses = []

    for i in range(24):
        stimulus = stimuli_list[i]
        response = Response.objects.create(
            test=test_session,
            stim=stimulus,
        )
        responses.append({
            "response_id": response.response_id,
            "stimulus": stimulus.stim_id,
        })

    return JsonResponse({"test_id": test_session.test_id, "responses": responses})


# a single json file that holds all the responses latencies everything, then a single view that parses and updates the db
# it would be best to just have one request for all the responses after a test is recorded


@csrf_exempt  # Disable CSRF for simplicity (use proper authentication in production)
def record_responses_bulk(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            responses_data = data.get("responses", [])

            if not responses_data:
                return JsonResponse({"error": "No responses provided."}, status=400)

            with transaction.atomic():  # Ensures all updates succeed or none do
                for response_entry in responses_data:
                    response_id = response_entry.get("response_id")
                    user_response = response_entry.get("response")
                    latency = response_entry.get("latency")
                    is_correct = response_entry.get("is_correct")

                    response = get_object_or_404(Response, response_id=response_id)
                    response.response = user_response
                    response.latency = latency
                    response.is_correct = is_correct
                    response.save()

                    test_session = response.test

                stats = test_session.response_set.aggregate(
                    avg_latency=models.Avg("latency"),
                    total_responses=models.Count("response_id"),
                    correct_responses=models.Count("response_id", filter=models.Q(is_correct=True))
                )
                test_session.avg_latency = stats["avg_latency"]
                test_session.accuracy = (stats["correct_responses"] / stats["total_responses"]) * 100 if stats[
                    "total_responses"] else 0
                test_session.save()

            return JsonResponse({"message": "Responses recorded successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)
=======
from django.shortcuts import render
from django.http import Http404
from .models import Computed
from django.utils import timezone


# Create your views here.

def get_divisor(n):
    #Returns a divisor of n if it's not prime, else None
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return i
    return None

def isprime(request, number):
    #Django view to check if a number is prime
    number = int(number)
    divisor = get_divisor(number)
    
    context = {
        "number": number,
        "isprime": divisor is None,

    }

     # Only add "divisor" if the number is NOT prime
    if divisor:
        context["divisor"] = divisor

    # Returns HTML 
    return render(request, "basic/prime.html", context)


def hello(request):
    # Return some HTML
    return render(request, "basic/helloworld.html", {})


# Computation function
def compute(request, value):
    try:
        input = int(value)
        precomputed = Computed.objects.filter(input=input)
        if precomputed.count() == 0:  # The answer for this input has not been computed
            # Compute the answer
            answer = input * input
            time_computed = timezone.now()
            # Save it into the database
            computed = Computed(
                input=input, 
                output=answer,
                time_computed=time_computed
            )
            computed.save() # Store it into the database
        else: 
            computed = precomputed[0] 
        
        return render (
            request,
            "basic/compute.html",
            {
                'input': input,
                'output': computed.output,
                'time_computed': computed.time_computed.strftime("%m-%d-%Y %H:%M:%S UTC")
            }
        )
    except:
        raise Http404(f"Invalid input: {value}")


    
>>>>>>> djangostarter/Amyr-Final-Prog-Branch
