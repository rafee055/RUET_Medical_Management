from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Doctor(models.Model):
    name = models.CharField(max_length=50)
    mobile = models.IntegerField()
    special = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)
    experience = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_days = models.CharField(max_length=100, default="Monday,Tuesday,Wednesday,Thursday,Friday")
    available_time = models.CharField(max_length=100, default="9:00-17:00")

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    mobile = models.IntegerField(null=True)
    address = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    PAYMENT_CHOICES = [
        ('bkash', 'bKash'),
        ('rocket', 'Rocket'),
        ('dbbl', 'DBBL'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('cash', 'Cash'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date1 = models.DateField()
    time1 = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='bkash')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    notification_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.doctor.name + "--" + self.patient.name

    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='user_profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.user.username

class MedicalTest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g., 30 minutes, 1 hour")
    preparation = models.TextField(blank=True, null=True, help_text="Any preparation required before the test")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TestBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    PAYMENT_CHOICES = [
        ('bkash', 'bKash'),
        ('rocket', 'Rocket'),
        ('dbbl', 'DBBL'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('cash', 'Cash'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(MedicalTest, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='bkash')
    result_pdf = models.FileField(upload_to='test_results/', null=True, blank=True)
    result_uploaded_at = models.DateTimeField(null=True, blank=True)
    notification_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.patient.name} - {self.test.name} ({self.date})"

    class Meta:
        ordering = ['-created_at']

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    manufacturer = models.CharField(max_length=100)
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='medicine_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class MedicineOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    payment_method = models.CharField(max_length=20, choices=[
        ('bkash', 'bKash'),
        ('rocket', 'Rocket'),
        ('dbbl', 'DBBL'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('cash', 'Cash'),
    ], default='bkash')
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('done', 'Done')], default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.medicine.name}"

    class Meta:
        ordering = ['-order_date']

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('test', 'Test'),
        ('medicine', 'Medicine'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    related_id = models.PositiveIntegerField()  # ID of the appointment, test, or medicine order
    method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.payment_type} - {self.method} - {self.amount}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    coordinates = models.CharField(max_length=50, blank=True, null=True)  # Format: "latitude,longitude"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
