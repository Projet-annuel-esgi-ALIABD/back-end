from django.db import models

# Create your models here.
class RefIndicator(models.Model):
    code = models.CharField(max_length=16, primary_key=True)
    label = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "ref_indicator"

class AlertThreshold(models.Model):
    indicator = models.ForeignKey('RefIndicator', on_delete=models.CASCADE)
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
    class Meta:
        db_table = "alerte"
