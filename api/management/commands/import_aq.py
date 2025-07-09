import os
import requests
from django.core.management.base import BaseCommand
from datetime import datetime, timezone, timedelta
from api.models import AirQualityMeasurement

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

class Command(BaseCommand):
    help = 'Importe les données de qualité de l’air (6 derniers mois, sans doublon)'

    def handle(self, *args, **kwargs):
        lat = 45.75
        lon = 4.85
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=182)

        url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
        params = {
            "lat": lat,
            "lon": lon,
            "start": int(start_dt.timestamp()),
            "end": int(end_dt.timestamp()),
            "appid": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json().get("list", [])

        # Préparer toutes les identités à vérifier (pour éviter les doublons)
        dt_list = [
            datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            for item in data
        ]
        existing = set(
            AirQualityMeasurement.objects.filter(
                latitude=lat,
                longitude=lon,
                datetime_utc__in=dt_list
            ).values_list("datetime_utc", flat=True)
        )

        to_create = []
        for item in data:
            m = item["main"]
            c = item["components"]
            dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            if dt not in existing:
                to_create.append(AirQualityMeasurement(
                    latitude=lat,
                    longitude=lon,
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

        AirQualityMeasurement.objects.bulk_create(to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"{len(to_create)} mesures importées."))
