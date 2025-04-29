from django.core.management.base import BaseCommand
from hospital.models import MedicalTest

class Command(BaseCommand):
    help = 'Populates the database with common medical tests'

    def handle(self, *args, **kwargs):
        tests = [
            {
                'name': 'Complete Blood Count (CBC)',
                'description': 'A blood test that measures different components of blood including red blood cells, white blood cells, and platelets.',
                'price': 50.00,
                'duration': '30 minutes',
                'preparation': 'No special preparation required.'
            },
            {
                'name': 'Blood Glucose Test',
                'description': 'Measures the amount of glucose (sugar) in your blood to screen for diabetes or monitor blood sugar levels.',
                'price': 35.00,
                'duration': '15 minutes',
                'preparation': 'Fasting for 8 hours before the test is required.'
            },
            {
                'name': 'Lipid Panel',
                'description': 'Measures cholesterol and triglyceride levels in your blood to assess heart disease risk.',
                'price': 75.00,
                'duration': '30 minutes',
                'preparation': 'Fasting for 12 hours before the test is required.'
            },
            {
                'name': 'Thyroid Function Test',
                'description': 'Measures thyroid hormone levels to evaluate thyroid function and diagnose thyroid disorders.',
                'price': 90.00,
                'duration': '30 minutes',
                'preparation': 'No special preparation required.'
            },
            {
                'name': 'Liver Function Test',
                'description': 'Measures various proteins and enzymes to assess liver health and function.',
                'price': 85.00,
                'duration': '30 minutes',
                'preparation': 'Fasting for 8 hours before the test is recommended.'
            },
            {
                'name': 'Kidney Function Test',
                'description': 'Measures creatinine and other markers to evaluate kidney function.',
                'price': 65.00,
                'duration': '30 minutes',
                'preparation': 'No special preparation required.'
            },
            {
                'name': 'Vitamin D Test',
                'description': 'Measures the level of vitamin D in your blood to assess bone health and immune function.',
                'price': 95.00,
                'duration': '30 minutes',
                'preparation': 'No special preparation required.'
            },
            {
                'name': 'Hemoglobin A1C',
                'description': 'Measures average blood sugar levels over the past 2-3 months, used to diagnose and monitor diabetes.',
                'price': 45.00,
                'duration': '15 minutes',
                'preparation': 'No special preparation required.'
            },
            {
                'name': 'Urinalysis',
                'description': 'Analyzes urine for various substances to detect kidney problems, urinary tract infections, and other conditions.',
                'price': 40.00,
                'duration': '20 minutes',
                'preparation': 'Clean catch urine sample required.'
            },
            {
                'name': 'Chest X-Ray',
                'description': 'Imaging test to examine the chest, lungs, heart, and blood vessels.',
                'price': 120.00,
                'duration': '15 minutes',
                'preparation': 'Remove jewelry and metal objects from the chest area.'
            }
        ]

        for test_data in tests:
            MedicalTest.objects.get_or_create(
                name=test_data['name'],
                defaults={
                    'description': test_data['description'],
                    'price': test_data['price'],
                    'duration': test_data['duration'],
                    'preparation': test_data['preparation']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated medical tests')) 