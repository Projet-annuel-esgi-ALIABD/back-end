from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

@swagger_auto_schema(
    method='get',
    operation_description="Healthcheck endpoint",
    responses={200: "Service is running"},
    tags=['Healthcheck']
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def healthcheck(request):
    return JsonResponse({"status": "ok"})