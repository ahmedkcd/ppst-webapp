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


    