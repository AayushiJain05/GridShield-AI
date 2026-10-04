from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import ConsumerRecord


class DashboardUploadTests(TestCase):
    def test_dashboard_accepts_csv_with_non_numeric_metadata_columns(self):
        csv_bytes = b"consumer_id,consumer_name,meter_number,area,day_1,day_2,day_3,cons_no,flag\n"
        csv_bytes += b"CUST-01,Alice,MTR-01,Feeder-A,10,20,30,ABC123,1\n"
        csv_bytes += b"CUST-02,Bob,MTR-02,Feeder-B,5,,15,DEF456,0\n"

        response = self.client.post(
            '/',
            {'csv_file': SimpleUploadedFile('meter_data.csv', csv_bytes, content_type='text/csv')},
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(ConsumerRecord.objects.count(), 2)
        record = ConsumerRecord.objects.order_by('consumer_id').first()
        self.assertLessEqual(len(record.shap_explanation), 7)
        self.assertTrue(record.shap_explanation)
        self.assertTrue(record.anomaly_calendar)
        self.assertIn(b'Why was this consumer flagged?', response.content)
        self.assertIn(b'Monthly anomaly timeline', response.content)
