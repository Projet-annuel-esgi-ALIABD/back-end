from datetime import timedelta

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models import AirQualityMeasurement
from api.utils.aq_utils import get_last_10h_aq

class Last10HoursAQView(APIView):
    @swagger_auto_schema(
        tags=['Air Quality'],
    )
    def get(self, request):
        try:
            data = get_last_10h_aq()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LastMonthAQView(APIView):
    @swagger_auto_schema(
        tags=['Air Quality'],
    )
    def get(self, request):
        now = timezone.now()
        month_ago = now - timedelta(days=31)
        qs = AirQualityMeasurement.objects.filter(datetime_utc__gte=month_ago).order_by('datetime_utc')
        data = [
            {
                "datetime": aq.datetime_utc.isoformat(),
                "aqi": aq.aqi,
                "co": aq.co,
                "no": aq.no,
                "no2": aq.no2,
                "o3": aq.o3,
                "so2": aq.so2,
                "pm2_5": aq.pm2_5,
                "pm10": aq.pm10,
                "nh3": aq.nh3,
            }
            for aq in qs
        ]
        return Response(data, status=status.HTTP_200_OK)