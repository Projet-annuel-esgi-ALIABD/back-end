import os
import requests

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

class CurrentWeatherView(APIView):
    @swagger_auto_schema(
        tags=['Weather']
    )
    def get(self, request):
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": 45.75,
                "lon": 4.85,
                "appid": api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return Response(data, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )