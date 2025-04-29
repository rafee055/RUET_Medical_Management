from hospital.models import Medicine
from django.utils import timezone

sample_medicines = [
    {
        'name': 'Paracetamol',
        'description': 'Pain reliever and fever reducer.',
        'price': 10.00,
        'quantity': 100,
        'manufacturer': 'ACME Pharma',
        'expiry_date': '2025-12-31',
    },
    {
        'name': 'Ibuprofen',
        'description': 'Nonsteroidal anti-inflammatory drug (NSAID).',
        'price': 15.00,
        'quantity': 50,
        'manufacturer': 'HealthCorp',
        'expiry_date': '2026-06-30',
    },
    {
        'name': 'Amoxicillin',
        'description': 'Antibiotic used to treat bacterial infections.',
        'price': 25.00,
        'quantity': 30,
        'manufacturer': 'BioMed',
        'expiry_date': '2025-09-15',
    },
    {
        'name': 'Cetirizine',
        'description': 'Antihistamine for allergy relief.',
        'price': 8.00,
        'quantity': 200,
        'manufacturer': 'AllergyFree',
        'expiry_date': '2026-01-01',
    },
    {
        'name': 'Metformin',
        'description': 'Used to treat type 2 diabetes.',
        'price': 12.00,
        'quantity': 80,
        'manufacturer': 'Diabetix',
        'expiry_date': '2025-11-20',
    },
    {
        'name': 'Aspirin',
        'description': 'Pain reliever and anti-inflammatory.',
        'price': 18.00,
        'quantity': 120,
        'manufacturer': 'FuturePharma',
        'expiry_date': '2027-12-31',
    },
]

for med in sample_medicines:
    Medicine.objects.get_or_create(
        name=med['name'],
        defaults=med
    )
print('Sample medicines added.') 