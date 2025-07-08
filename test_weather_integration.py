#!/usr/bin/env python3
"""
Test script to verify weather prediction integration
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_city.settings')
django.setup()

# Test the weather prediction service
def test_weather_prediction():
    """Test the weather prediction functionality"""
    from api.services.weather_service import WeatherPredictionService
    
    # You'll need to set your API key here
    api_key = os.environ.get('METEOFRANCE_API_KEY')
    
    if not api_key:
        print("❌ Error: METEOFRANCE_API_KEY environment variable not set")
        print("Please set it in your environment or .env file")
        return
    
    try:
        print("🌤️  Testing Weather Prediction Service...")
        
        # Create service
        weather_service = WeatherPredictionService(api_key)
        
        # Test single prediction
        print("\n📊 Testing single prediction (TX - Maximum Temperature)...")
        result = weather_service.predict_weather('TX', 1)
        
        if result['success']:
            prediction = result['prediction']
            print(f"✅ Prediction successful!")
            print(f"   Feature: {prediction['feature']}")
            print(f"   Predicted value: {prediction['value']} {prediction['unit']}")
            print(f"   Days ahead: {prediction['days_ahead']}")
            print(f"   Prediction date: {prediction['prediction_date']}")
        else:
            print(f"❌ Prediction failed: {result['error']}")
        
        # Test multiple predictions
        print("\n📊 Testing multiple predictions...")
        result = weather_service.get_multiple_predictions(['TX', 'TN', 'RR'], 1)
        
        if result['success']:
            print(f"✅ Multiple predictions successful!")
            for feature, pred_result in result['predictions'].items():
                if pred_result['success']:
                    pred = pred_result['prediction']
                    print(f"   {pred['feature']}: {pred['value']} {pred['unit']}")
                else:
                    print(f"   {feature}: Failed - {pred_result['error']}")
        else:
            print(f"❌ Multiple predictions failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Test the API endpoints"""
    from django.test import Client
    from django.contrib.auth.models import User
    
    print("\n🔗 Testing API Endpoints...")
    
    # Create test client
    client = Client()
    
    # Test healthcheck
    response = client.get('/api/healthcheck/')
    if response.status_code == 200:
        print("✅ Healthcheck endpoint working")
    else:
        print(f"❌ Healthcheck failed: {response.status_code}")
    
    # You would need to test the prediction endpoints with authentication
    print("ℹ️  Weather prediction endpoints require authentication")
    print("   Use /api/predict/weather/ and /api/predict/weather/multiple/")

if __name__ == "__main__":
    print("🚀 Starting Weather Prediction Integration Test")
    print("=" * 50)
    
    test_weather_prediction()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")
    print("\nNext steps:")
    print("1. Set METEOFRANCE_API_KEY in your environment")
    print("2. Run: python manage.py train_weather_models")
    print("3. Start the Django server: python manage.py runserver")
    print("4. Test the API endpoints with authentication")
