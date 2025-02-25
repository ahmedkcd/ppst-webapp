from django.shortcuts import render
from django.http import Http404
from .models import Computed
from django.utils import timezone

# Create your views here.
def isprime(request, value):
    divisor = 0
    isprime = True

    input = int(value)
    if(input < 2):
        isprime = True
    else:
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                divisor = i
                isprime = False

    # Return some html
        return render (
            request,
            "basic/isprime.html",
            {
                'value': value,
                'isprime': isprime,
                'divisor': divisor,
            }
        )


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


    