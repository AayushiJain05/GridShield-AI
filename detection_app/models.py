from django.db import models

class ConsumerRecord(models.Model):
    consumer_id = models.CharField(max_length=50)
    consumer_name = models.CharField(max_length=100)
    meter_number = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    avg_consumption = models.FloatField()
    peak_consumption = models.FloatField()
    prediction_result = models.CharField(max_length=20)
    theft_probability = models.FloatField()
    shap_explanation = models.JSONField(default=list, blank=True)
    anomaly_calendar = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consumer_id} - {self.prediction_result}"