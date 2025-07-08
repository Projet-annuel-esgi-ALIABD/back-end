from django.db import models

ALERT_TYPE_CHOICES = [
    ("info", "Information"),
    ("warning", "Avertissement"),
    ("critical", "Critique"),
]

# Create your models here.
class RefIndicator(models.Model):
    code = models.CharField(max_length=16, primary_key=True)
    label = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "ref_indicator"

class AlertThreshold(models.Model):
    indicator = models.ForeignKey('RefIndicator', to_field="code", db_column="indicator_code", on_delete=models.CASCADE)
    threshold_value = models.FloatField()
    active = models.BooleanField(default=True)
    class Meta:
        db_table = "alert_threshold"

class Alerte(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_by = models.CharField(max_length=16, choices=[('auto', 'Automatique'), ('admin', 'Administrateur')])
    threshold = models.ForeignKey('AlertThreshold', on_delete=models.PROTECT, null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    message = models.TextField()
    alert_type = models.CharField(max_length=16, choices=ALERT_TYPE_CHOICES, default="info")
    class Meta:
        db_table = "alerte"

class AirQualityMeasurement(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    datetime_utc = models.DateTimeField()
    aqi = models.IntegerField()
    co = models.FloatField()
    no = models.FloatField()
    no2 = models.FloatField()
    o3 = models.FloatField()
    so2 = models.FloatField()
    pm2_5 = models.FloatField()
    pm10 = models.FloatField()
    nh3 = models.FloatField()

    class Meta:
        db_table = "air_quality_measurement"
        indexes = [
            models.Index(fields=["latitude", "longitude", "datetime_utc"]),
        ]
        unique_together = ("latitude", "longitude", "datetime_utc")