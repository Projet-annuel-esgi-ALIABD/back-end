import os
import requests
from django.core.management.base import BaseCommand
from datetime import datetime, timezone, timedelta
from api.models import AirQualityMeasurement
from django import db

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

class Command(BaseCommand):
    help = "Importe la mesure de qualité de l'air pour la dernière heure."

    def handle(self, *args, **kwargs):
        db.close_old_connections()
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(hours=1)
        url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
        params = {
            "lat": 45.75,
            "lon": 4.85,
            "start": int(start_dt.timestamp()),
            "end": int(end_dt.timestamp()),
            "appid": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json().get("list", [])
        to_create = []
        for item in data:
            m = item["main"]
            c = item["components"]
            dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            exists = AirQualityMeasurement.objects.filter(
                latitude=45.75,
                longitude=4.85,
                datetime_utc=dt
            ).exists()
            if not exists:
                to_create.append(AirQualityMeasurement(
                    latitude=45.75,
                    longitude=4.85,
                    datetime_utc=dt,
                    aqi=m["aqi"],
                    co=c["co"],
                    no=c["no"],
                    no2=c["no2"],
                    o3=c["o3"],
                    so2=c["so2"],
                    pm2_5=c["pm2_5"],
                    pm10=c["pm10"],
                    nh3=c["nh3"],
                ))
        AirQualityMeasurement.objects.bulk_create(to_create, batch_size=100)
        msg = (
            "--- CRONJOB IMPORT AQ ---\n"
            f"{len(to_create)} mesures importées.)\n"
        )
        self.stdout.write(self.style.SUCCESS(msg))