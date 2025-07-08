from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RegisterView, UserDetailView, LogoutView, healthcheck
from api.views.alert_treshold import AlertThresholdView
from api.views.alerte import AlerteView
from api.views.auth import LoginView, CustomTokenRefreshView
from api.views.air_quality import Last10HoursAQView, LastMonthAQView
from api.views.predict_air_quality import AirQualityPredictView
from api.views.weather_prediction import WeatherPredictionView

router = DefaultRouter()
router.register(r'alerte', AlerteView, basename='alerte')
router.register(r'alert-treshold', AlertThresholdView, basename='alert_threshold')

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
    path('predict/weather/', WeatherPredictionView.as_view(), name='predict_weather'),
    # OpenWeatherMap
    path('aq/last-10h/', Last10HoursAQView.as_view(), name='last_10h_aq'),
    path('aq/last-month/', LastMonthAQView.as_view(), name='last_month_aq'),
    # CRUD views
    path('', include(router.urls)),
]
