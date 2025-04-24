from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view


@swagger_auto_schema(
    method='get',
    operation_description="Healthcheck endpoint",
    responses={200: "Service is running"},
    tags=['Healthcheck']
)
@api_view(['GET'])
def healthcheck(request):
    return JsonResponse({"status": "ok"})