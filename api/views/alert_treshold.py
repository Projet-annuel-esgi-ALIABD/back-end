from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import AlertThreshold, RefIndicator
from api.serializers import AlertThresholdSerializer

# AlertThreshold CRUD
class AlertThresholdView(viewsets.ViewSet):
    @swagger_auto_schema(tags=['Alerte Threshold'])
    def list(self, request):
        qs = AlertThreshold.objects.filter(active=True)
        serializer = AlertThresholdSerializer(qs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Alerte Threshold'])
    def retrieve(self, request, pk=None):
        try:
            obj = AlertThreshold.objects.get(pk=pk, active=True)
        except AlertThreshold.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AlertThresholdSerializer(obj)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Alerte Threshold'],
        request_body = AlertThresholdSerializer
    )
    def create(self, request):
        indicator_code = request.data.get("indicator")
        threshold_value = request.data.get("threshold_value")
        if not indicator_code or threshold_value is None:
            return Response({"detail": "indicator and threshold_value required"}, status=400)
        # Inactive previous active threshold for this indicator
        AlertThreshold.objects.filter(indicator__code=indicator_code, active=True).update(active=False)
        indicator = RefIndicator.objects.get(code=indicator_code)
        threshold = AlertThreshold.objects.create(
            indicator=indicator,
            threshold_value=threshold_value,
            active=True
        )
        serializer = AlertThresholdSerializer(threshold)
        return Response(serializer.data, status=201)

    @swagger_auto_schema(tags=['Alerte Threshold'])
    def destroy(self, request, pk=None):
        try:
            threshold = AlertThreshold.objects.get(pk=pk)
        except AlertThreshold.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        threshold.active = False
        threshold.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
