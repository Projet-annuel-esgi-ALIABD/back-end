import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.services.weather_service import WeatherPredictionService


class WeatherPredictionView(APIView):
    """
    View for weather prediction using the integrated model
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Predict weather for next days using machine learning model",
        manual_parameters=[
            openapi.Parameter(
                "feature",
                openapi.IN_QUERY,
                description="Weather feature to predict: TX (max temp), TN (min temp), RR (precipitation), TM (avg temp), TAMPLI (temp amplitude)",
                type=openapi.TYPE_STRING,
                default="TX",
            ),
            openapi.Parameter(
                "days",
                openapi.IN_QUERY,
                description="Number of days ahead to predict (1-7)",
                type=openapi.TYPE_INTEGER,
                default=1,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Weather prediction successful",
                examples={
                    "application/json": {
                        "success": True,
                        "prediction": {
                            "value": 22.5,
                            "unit": "°C",
                            "feature": "Maximum Temperature",
                            "days_ahead": 1,
                            "prediction_date": "2025-07-09",
                        },
                        "context": {
                            "latest_data": {"TX": 20.3, "TN": 12.1, "RR": 0.0},
                            "station_id": "69123002",
                            "model_info": {
                                "target_feature": "TX",
                                "days_to_predict": 1,
                            },
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request or prediction failed",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Failed to fetch recent weather data",
                        "prediction": None,
                        "context": None,
                    }
                },
            ),
        },
        tags=["Weather Prediction"],
    )
    def get(self, request):
        """
        Get weather prediction for specified feature and time horizon
        """
        try:
            # Get query parameters
            feature = request.query_params.get("feature", "TX")
            days = int(request.query_params.get("days", 1))

            # Validate parameters
            valid_features = ["TX", "TN", "RR", "TM", "TAMPLI"]
            if feature not in valid_features:
                return Response(
                    {
                        "success": False,
                        "error": f"Invalid feature. Must be one of: {valid_features}",
                        "prediction": None,
                        "context": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if days < 1 or days > 7:
                return Response(
                    {
                        "success": False,
                        "error": "Days must be between 1 and 7",
                        "prediction": None,
                        "context": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get API key from environment
            api_key = os.environ.get("METEOFRANCE_API_KEY")
            if not api_key:
                return Response(
                    {
                        "success": False,
                        "error": "Météo France API key not configured",
                        "prediction": None,
                        "context": None,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Create prediction service
            weather_service = WeatherPredictionService(api_key)

            # Make prediction
            result = weather_service.predict_weather(feature, days)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "error": f"Invalid parameters: {str(e)}",
                    "prediction": None,
                    "context": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "prediction": None,
                    "context": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
