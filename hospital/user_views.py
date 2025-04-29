from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Doctor, Patient, Appointment, UserProfile, MedicalTest, TestBooking, MedicineOrder
from django.contrib import messages
from datetime import datetime, timedelta, time
from django.core.paginator import Paginator

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        gender = request.POST['gender']
        mobile = request.POST['mobile']
        address = request.POST['address']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('user_register')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, phone_number=mobile, gender=gender, address=address)
        Patient.objects.create(user=user, name=name, gender=gender, mobile=mobile, address=address)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('user_login')
        
    return render(request, 'user/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user is not None and not user.is_staff:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            
    return render(request, 'user/login.html')

@login_required
def user_dashboard(request):
    # Try to get the patient record, create one if it doesn't exist
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        # Create a patient record if it doesn't exist
        patient = Patient.objects.create(
            user=request.user,
            name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            gender="Not Specified",  # Default value
            mobile=None,  # Can be updated later
            address="Not Specified"  # Default value
        )
        messages.info(request, "Please update your profile information.")
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-date1', '-time1')
    test_bookings = TestBooking.objects.filter(patient=patient).order_by('-date', '-time')
    # Add recent medicine orders for this user
    medicine_orders = MedicineOrder.objects.filter(user=request.user).order_by('-order_date')[:5]
    # Check for any new notifications
    new_appointments = appointments.filter(status__in=['confirmed', 'rejected'], notification_seen=False)
    new_test_bookings = test_bookings.filter(status__in=['confirmed', 'cancelled'], notification_seen=False)
    # Mark notifications as seen
    if new_appointments.exists():
        new_appointments.update(notification_seen=True)
    if new_test_bookings.exists():
        new_test_bookings.update(notification_seen=True)
    context = {
        'patient': patient,
        'appointments': appointments,
        'test_bookings': test_bookings,
        'new_appointments': new_appointments,
        'new_test_bookings': new_test_bookings,
        'medicine_orders': medicine_orders
    }
    return render(request, 'user/dashboard.html', context)

@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'user/doctor_list.html', {'doctors': doctors})

def generate_time_slots(time_range_str, interval=30):
    """Generate time slots between start and end time with given interval in minutes"""
    try:
        # Split the time range string (format: "HH:MM-HH:MM")
        start_time_str, end_time_str = time_range_str.split('-')
        
        # Parse time strings (format: "HH:MM")
        start_time = datetime.strptime(start_time_str.strip(), "%H:%M").time()
        end_time = datetime.strptime(end_time_str.strip(), "%H:%M").time()
        
        slots = []
        current = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        
        while current <= end:
            slots.append(current.time().strftime("%H:%M"))
            current += timedelta(minutes=interval)
            
        return slots
    except:
        # Return default time slots if time format is invalid
        return ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]

@login_required
def book_appointment(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    patient = Patient.objects.get(user=request.user)
    available_times = generate_time_slots(doctor.available_time)
    if request.method == 'POST':
        date = request.POST['date']
        time = request.POST['time']
        symptoms = request.POST['symptoms']
        payment_method = request.POST.get('payment_method', 'bkash')
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        if appointment_date < datetime.now().date():
            messages.error(request, 'Please select a future date')
            return redirect('book_appointment', doctor_id=doctor_id)
        day_name = appointment_date.strftime('%A')
        if day_name not in doctor.available_days:
            messages.error(request, f'Doctor is not available on {day_name}s')
            return redirect('book_appointment', doctor_id=doctor_id)
        if Appointment.objects.filter(
            doctor=doctor,
            date1=date,
            time1=time,
            status__in=['pending', 'confirmed']
        ).exists():
            messages.error(request, 'This time slot is already booked. Please choose another time.')
            return redirect('book_appointment', doctor_id=doctor_id)
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date1=date,
            time1=time,
            symptoms=symptoms,
            payment_method=payment_method,
            status='pending'
        )
        # Create Payment record
        from hospital.models import Payment
        payment = Payment.objects.create(
            user=request.user,
            payment_type='appointment',
            related_id=appointment.id,
            method=payment_method,
            amount=doctor.consultation_fee,
            status='pending'
        )
        return redirect('payment_interface', payment_id=payment.id)
    context = {
        'doctor': doctor,
        'patient': patient,
        'available_days': doctor.available_days.split(','),
        'available_times': available_times,
        'today': datetime.now().date()
    }
    return render(request, 'user/book_appointment.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, patient__user=request.user)
        if appointment.status in ['pending', 'confirmed']:
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, 'Appointment cancelled successfully!')
        else:
            messages.error(request, 'This appointment cannot be cancelled.')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
    return redirect('user_dashboard')

@login_required(login_url='userlogin')
def test_list(request):
    tests = MedicalTest.objects.filter(is_active=True).order_by('name')
    
    paginator = Paginator(tests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tests': page_obj,
        'page_obj': page_obj,
        'is_test_list': True  # Flag to differentiate from my_test_bookings view
    }
    return render(request, 'user/test_list.html', context)

@login_required(login_url='userlogin')
def book_test(request, test_id):
    test = get_object_or_404(MedicalTest, id=test_id)
    patient = Patient.objects.get(user=request.user)
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        notes = request.POST.get('notes')
        payment_method = request.POST.get('payment_method', 'bkash')
        booking = TestBooking.objects.create(
            patient=patient,
            test=test,
            date=date,
            time=time,
            status='pending',
            payment_method=payment_method
        )
        # Create Payment record
        from hospital.models import Payment
        payment = Payment.objects.create(
            user=request.user,
            payment_type='test',
            related_id=booking.id,
            method=payment_method,
            amount=test.price,
            status='pending'
        )
        return redirect('payment_interface', payment_id=payment.id)
    return render(request, 'user/book_test.html', {'test': test})

@login_required(login_url='userlogin')
def cancel_test(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, patient__user=request.user)
    
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Test booking cancelled successfully!')
    else:
        messages.error(request, 'Only pending test bookings can be cancelled.')
    
    return redirect('user_dashboard')

@login_required(login_url='userlogin')
def my_test_bookings(request):
    patient = Patient.objects.get(user=request.user)
    test_bookings = TestBooking.objects.filter(patient=patient).order_by('-date', '-time')
    
    paginator = Paginator(test_bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'test_bookings': page_obj,
        'page_obj': page_obj,
        'is_test_list': False  # This ensures we show the bookings view
    }
    return render(request, 'user/test_list.html', context)

@login_required
def user_payment_history(request):
    from hospital.models import Payment
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/payment_history.html', {'payments': payments}) 