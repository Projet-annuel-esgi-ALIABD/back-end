from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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