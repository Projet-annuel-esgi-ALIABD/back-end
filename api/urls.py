from django.urls import path

from api.views import RegisterView, UserDetailView, LogoutView, healthcheck
from api.views.auth import LoginView, CustomTokenRefreshView

urlpatterns = [
    # Healthcheck
    path("healthcheck/", healthcheck, name="healthcheck"),
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    # User
    path('user/', UserDetailView.as_view(), name='user'),
]
