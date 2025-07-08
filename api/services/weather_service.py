import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from api.models_ai.weather.weather_prediction_model import WeatherPredictionModel


class MeteoFranceAPI:
    """
    A class to interact with the Météo France API for climatological data
    """

    def __init__(self, api_key):
        """
        Initialize with your API credentials

        Args:
            api_key (str): Your Météo France API key
        """
        self.api_key = api_key
        self.base_url = "https://public-api.meteofrance.fr/public/DPClim/v1"
        self.headers = {
            "apikey": f"{self.api_key}",
            "Content-Type": "application/json",
        }

    def create_data_order(
        self, station_id, start_date, end_date, frequency="quotidienne"
    ):
        """
        Create an order for climate data

        Args:
            station_id (str): ID of the weather station
            start_date (str): Start date in ISO 8601 format
            end_date (str): End date in ISO 8601 format
            frequency (str): Data frequency - "quotidienne", "horaire", or "infrahoraire-6m"

        Returns:
            str: Order ID if successful, None otherwise
        """
        url = f"{self.base_url}/commande-station/{frequency}?id-station={station_id}&date-deb-periode={start_date}&date-fin-periode={end_date}"
        payload = {}
        response = requests.get(url, headers=self.headers, json=payload)

        if response.status_code == 202:
            try:
                order_id = response.json()["elaboreProduitAvecDemandeResponse"][
                    "return"
                ]
                return order_id
            except KeyError:
                print(f"Unexpected response format: {response.text}")
                return None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def download_data(self, order_id, max_retries=5, retry_delay=10):
        """
        Download ordered climate data

        Args:
            order_id (str): Order ID from create_data_order
            max_retries (int): Maximum number of retries
            retry_delay (int): Delay in seconds between retries

        Returns:
            str: Data as string if successful, None otherwise
        """
        url = f"{self.base_url}/commande/fichier?id-cmde={order_id}"

        for attempt in range(max_retries):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 201:  # Data is ready
                return response.content.decode("utf-8")
            elif response.status_code == 204:  # Still processing
                print(
                    f"Order {order_id} is still processing. Retry {attempt+1}/{max_retries}"
                )
                import time

                time.sleep(retry_delay)
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        print(f"Max retries reached for order {order_id}")
        return None

    def get_recent_data(self, station_id, days_back=30):
        """
        Get recent weather data for a station

        Args:
            station_id (str): ID of the weather station
            days_back (int): Number of days back to fetch data

        Returns:
            pd.DataFrame: Recent weather data
        """
        end_date = datetime.now() - timedelta(
            days=2
        )  # 2 days ago to ensure data availability
        start_date = end_date - timedelta(days=days_back)

        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Fetching recent data from {start_date_str} to {end_date_str}")

        # Create order
        order_id = self.create_data_order(station_id, start_date_str, end_date_str)

        if order_id:
            # Download data
            data_str = self.download_data(order_id)

            if data_str:
                # Convert to DataFrame
                from io import StringIO

                df = pd.read_csv(StringIO(data_str), sep=";")

                # Convert date column to datetime
                if "DATE" in df.columns:
                    df["DATE"] = pd.to_datetime(df["DATE"])

                return df

        return None


class WeatherPredictionService:
    """
    Service to integrate weather data fetching with prediction model
    """

    def __init__(self, api_key, station_id="69123002"):
        """
        Initialize the weather prediction service

        Args:
            api_key (str): Météo France API key
            station_id (str): Weather station ID
        """
        self.api_key = api_key
        self.station_id = station_id
        self.meteo_api = MeteoFranceAPI(api_key)
        self.model = None

    def get_or_create_model(self, target_feature="TX", days_to_predict=1):
        """
        Get existing model or create/train a new one

        Args:
            target_feature (str): Feature to predict
            days_to_predict (int): Number of days ahead to predict

        Returns:
            WeatherPredictionModel: The prediction model
        """
        model_path = f"api/models_ai/weather/saved_models"

        # Try to load existing model
        model = WeatherPredictionModel(
            target_feature=target_feature, days_to_predict=days_to_predict
        )

        if model.load_model(model_path):
            print("Loaded existing model")
            return model

        # If no existing model, we need to train one
        # For now, we'll return a model that needs to be trained
        print("No existing model found. Model needs to be trained.")
        return model

    def predict_weather(self, target_feature="TX", days_to_predict=1):
        """
        Predict weather for the next days

        Args:
            target_feature (str): Feature to predict (TX, TN, RR, etc.)
            days_to_predict (int): Number of days ahead to predict

        Returns:
            dict: Prediction result with confidence metrics
        """
        try:
            # Get recent weather data
            recent_data = self.meteo_api.get_recent_data(self.station_id, days_back=30)

            if recent_data is None or recent_data.empty:
                raise ValueError("Failed to fetch recent weather data")

            # Get or create model
            model = self.get_or_create_model(target_feature, days_to_predict)

            if model.model is None:
                # Train model with recent data if no pre-trained model exists
                model.load_data_from_dataframe(recent_data)
                model.build_model()

                # Save the model for future use
                model_path = f"api/models_ai/weather/saved_models"
                model.save_model(model_path)

            # Make prediction
            prediction = model.make_prediction(recent_data)

            if prediction is None:
                raise ValueError("Failed to make prediction")

            # Get latest actual data for context
            latest_data = recent_data.iloc[-1].to_dict()

            # Determine prediction type
            feature_names = {
                "TX": "Maximum Temperature",
                "TN": "Minimum Temperature",
                "RR": "Precipitation",
                "TM": "Average Temperature",
                "TAMPLI": "Temperature Amplitude",
            }

            return {
                "success": True,
                "prediction": {
                    "value": round(prediction, 2),
                    "unit": (
                        "°C" if target_feature in ["TX", "TN", "TM", "TAMPLI"] else "mm"
                    ),
                    "feature": feature_names.get(target_feature, target_feature),
                    "days_ahead": days_to_predict,
                    "prediction_date": (
                        datetime.now() + timedelta(days=days_to_predict)
                    ).strftime("%Y-%m-%d"),
                },
                "context": {
                    "latest_data": latest_data,
                    "station_id": self.station_id,
                    "model_info": {
                        "target_feature": target_feature,
                        "days_to_predict": days_to_predict,
                    },
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prediction": None,
                "context": None,
            }

    def get_multiple_predictions(self, features=["TX", "TN", "RR"], days_to_predict=1):
        """
        Get predictions for multiple weather features

        Args:
            features (list): List of features to predict
            days_to_predict (int): Number of days ahead to predict

        Returns:
            dict: Multiple prediction results
        """
        results = {}

        for feature in features:
            results[feature] = self.predict_weather(feature, days_to_predict)

        return {
            "success": True,
            "predictions": results,
            "prediction_date": (
                datetime.now() + timedelta(days=days_to_predict)
            ).strftime("%Y-%m-%d"),
            "days_ahead": days_to_predict,
        }
