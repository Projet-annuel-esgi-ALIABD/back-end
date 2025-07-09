from django.core.management.base import BaseCommand
import requests
from django.utils import timezone
from api.models import AlertThreshold, Alerte
import os
from django import db

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

class Command(BaseCommand):
    help = "Vérifie les seuils d'alerte et crée une alerte si besoin."

    def handle(self, *args, **kwargs):
        db.close_old_connections()
        url = "https://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            "lat": 45.75,
            "lon": 4.85,
            "appid": API_KEY
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        components = data["list"][0]["components"]
        aqi = data["list"][0]["main"]["aqi"]

        thresholds = AlertThreshold.objects.filter(active=True)
        alerts_created = 0
        for threshold in thresholds:
            code = threshold.indicator.code
            if code == "aqi":
                value = aqi
            else:
                value = components.get(code)
            if value is not None and value >= threshold.threshold_value:
                Alerte.objects.create(
                    created_at=timezone.now(),
                    triggered_by="auto",
                    threshold=threshold,
                    value=value,
                    message=f"Threshold exceeded for {code}: {value} (threshold: {threshold.threshold_value})",
                    alert_type="critical"
                )
                alerts_created += 1
                msg = (
                    "--- CRONJOB ALERTE ---\n"
                    f"Valeurs mesurées : {components}\n"
                    f"AQI mesuré : {aqi}\n"
                    f"Nombre d'alertes créées : {alerts_created}\n"
                )
                self.stdout.write(self.style.SUCCESS(msg))