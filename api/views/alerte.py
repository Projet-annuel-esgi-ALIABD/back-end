from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from api.models import Alerte
from api.serializers import AlerteSerializer

class AlerteView(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer

    @swagger_auto_schema(tags=['Alerte'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Alerte'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Alerte'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Alerte'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Alerte'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Alerte'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
