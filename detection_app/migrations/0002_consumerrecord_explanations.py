from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumerrecord',
            name='shap_explanation',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='consumerrecord',
            name='anomaly_calendar',
            field=models.JSONField(blank=True, default=list),
        ),
    ]