from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import UserSerializer, RegisterSerializer, UserTokenObtainPairSerializer
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Inscrit un nouvel utilisateur",
        responses={201: "Utilisateur créé avec succès"},
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
    @swagger_auto_schema(
        operation_description="Retourne un JWT token d'authentification",
        responses={200: "JWT token obtenu avec succès"},
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Récupère les détails de l'utilisateur connecté",
        responses={200: "Détails de l'utilisateur récupérés avec succès"},
        tags=['User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Déconnecte l'utilisateur et invalide son token",
        responses={200: "Déconnexion réussie"},
        tags = ['Authentication']
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description="Rafraîchit un token JWT expiré",
        responses={200: "Token rafraîchi avec succès"},
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)