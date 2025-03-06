from django.urls import path
from django.http import JsonResponse


def healthcheck(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("healthcheck/", healthcheck, name="healthcheck"),
]
