from django.urls import path

from api.views import RegisterView, UserDetailView, LogoutView, healthcheck
from api.views.auth import LoginView, CustomTokenRefreshView
from api.views.air_quality import Last10HoursAQView
from api.views.predict_air_quality import AirQualityPredictView

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
    # Predict AI
    path('predict/air-quality/', AirQualityPredictView.as_view(), name='predict_air_quality'),
    # OpenWeatherMap
    path('aq/last-10h/', Last10HoursAQView.as_view(), name='last_10h_aq'),
]
