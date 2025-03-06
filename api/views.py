from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def healthcheck(request):
    """
    Simple healthcheck endpoint that returns a status OK response
    """
    return JsonResponse({"status": "ok"})
