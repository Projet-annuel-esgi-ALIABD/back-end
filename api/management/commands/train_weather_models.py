import os
from django.core.management.base import BaseCommand
from api.services.weather_service import WeatherPredictionService


class Command(BaseCommand):
    help = 'Pre-train weather prediction models with historical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--features',
            type=str,
            default='TX,TN,RR,TM,TAMPLI',
            help='Comma-separated list of features to train models for'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days ahead to predict'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain even if model already exists'
        )

    def handle(self, *args, **options):
        features = options['features'].split(',')
        days = options['days']
        force = options['force']
        
        # Get API key from environment
        api_key = os.environ.get('METEOFRANCE_API_KEY')
        if not api_key:
            self.stdout.write(
                self.style.ERROR('METEOFRANCE_API_KEY environment variable not set')
            )
            return
        
        # Create weather service
        weather_service = WeatherPredictionService(api_key)
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting model training for features: {features}')
        )
        
        for feature in features:
            feature = feature.strip()
            self.stdout.write(f'Training model for {feature}...')
            
            try:
                # Get recent data for training
                recent_data = weather_service.meteo_api.get_recent_data(
                    weather_service.station_id, 
                    days_back=365  # Use 1 year of data for training
                )
                
                if recent_data is None or recent_data.empty:
                    self.stdout.write(
                        self.style.WARNING(f'No data available for {feature}')
                    )
                    continue
                
                # Create and train model
                from api.models_ai.weather.weather_prediction_model import WeatherPredictionModel
                model = WeatherPredictionModel(
                    target_feature=feature,
                    days_to_predict=days
                )
                
                # Load data and train
                model.load_data_from_dataframe(recent_data)
                trained_model, metrics = model.build_model()
                
                # Save model
                model_path = f"api/models_ai/weather/saved_models"
                model.save_model(model_path)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Model for {feature} trained successfully. '
                        f'Test RMSE: {metrics["test_rmse"]:.2f}, '
                        f'Test R²: {metrics["test_r2"]:.4f}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to train model for {feature}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Model training completed!')
        )
