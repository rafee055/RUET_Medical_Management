from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,logout,login
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import MedicineForm
from django.core.mail import send_mail
from .payment_gateways import get_payment_gateway
from django.conf import settings
from django.http import JsonResponse
# Create your views here.


def About(request):
    return render(request,'about.html')

def Contact(request):
    return render(request,'contact.html')

def Index(request):
    if not request.user.is_staff:
        return redirect('login')
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    appointments = Appointment.objects.all()

    d=0;
    p=0;
    a=0;
    for i in doctors:
            d=d+1
    for i in patients:
            p=p+1
    for i in appointments:
            a=a+1
    d1 = {'d':d, 'p':p, 'a':a}

    doctor_count = Doctor.objects.count()
    patient_count = Patient.objects.count()
    appointment_count = Appointment.objects.count()
    test_count = MedicalTest.objects.filter(is_active=True).count()
    test_booking_count = TestBooking.objects.count()
    
    # Get test statistics
    pending_tests = TestBooking.objects.filter(status='pending').count()
    completed_tests = TestBooking.objects.filter(status='completed').count()
    confirmed_tests = TestBooking.objects.filter(status='confirmed').count()
    
    # Get recent test bookings
    recent_test_bookings = TestBooking.objects.select_related('patient', 'test').order_by('-created_at')[:5]

    # Medicine statistics
    total_medicines = Medicine.objects.count()
    low_stock_medicines = Medicine.objects.filter(quantity__lte=10).count()
    expired_medicines = Medicine.objects.filter(expiry_date__lt=timezone.now().date()).count()
    pending_orders = MedicineOrder.objects.filter(payment_status='done', status='pending').count()

    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'appointment_count': appointment_count,
        'test_count': test_count,
        'test_booking_count': test_booking_count,
        'pending_tests': pending_tests,
        'completed_tests': completed_tests,
        'confirmed_tests': confirmed_tests,
        'recent_test_bookings': recent_test_bookings,
        'total_medicines': total_medicines,
        'low_stock_medicines': low_stock_medicines,
        'expired_medicines': expired_medicines,
        'pending_orders': pending_orders,
    }
    return render(request, 'home.html', context)

def Register(request):
    import random, time
    if request.method == 'GET':
        if 'pending_registration' in request.session:
            del request.session['pending_registration']
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        gender = request.POST['gender']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('register')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('register')

        code = str(random.randint(100000, 999999))
        request.session['pending_registration'] = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'phone': phone,
            'gender': gender,
            'password': password1,
            'code': code,
            'timestamp': time.time()
        }
        send_mail(
            'Your RUET Medical Management Verification Code',
            f'Your verification code is: {code}\nThis code will expire in 5 minutes.',
            'noreply@ruetmedical.com',
            [email],
            fail_silently=False,
        )
        return redirect('verify_email')
    return render(request, 'register.html')

def UserLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            if user.is_staff:
                return redirect('home')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
            
    return render(request, 'login.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid admin credentials!')
            
    return render(request, 'admin_login.html')

def Logout(request):
    if request.user.is_authenticated:  # Ensure user is logged in
        logout(request)
    return redirect('login')


def View_Doctor(request):
    if not request.user.is_staff:
        return redirect('login')
    doc = Doctor.objects.all()
    d = {'doc':doc}
    return render(request,'view_doctor.html',d)


def Add_Doctor(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        n = request.POST['name']
        c = request.POST['contact']
        sp= request.POST['special']
        try:
            Doctor.objects.create(name=n,mobile=c,special=sp)
            error = "no"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'add_doctor.html', d)

def Delete_Doctor(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    try:
        doctor = Doctor.objects.get(id=pid)
        doctor.delete()
    except Doctor.DoesNotExist:
        pass
    return redirect('doctor_list')



def View_Patient(request):
    if not request.user.is_staff:
        return redirect('login')
    pat = Patient.objects.all()
    d = {'pat':pat}
    return render(request,'view_patient.html',d)


def Add_Patient(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        n = request.POST['name']
        g = request.POST['gender']
        m = request.POST['mobile']
        a= request.POST['address']
        try:
            Patient.objects.create(name=n,gender=g,mobile=m,address=a)
            error = "no"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'add_patient.html', d)

def Delete_Patient(request,pid):
    if not request.user.is_staff:
        return redirect('login')
    patient = Patient.objects.get(id=pid)
    patient.delete()
    return redirect('view_patient')



def View_Appointment(request):
    if not request.user.is_staff:
        return redirect('login')
    appoint = Appointment.objects.all().order_by('-date1', '-time1')
    d = {'appoint':appoint}
    return render(request,'view_appointment.html',d)

def Accept_Appointment(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    appointment = Appointment.objects.get(id=pid)
    appointment.status = 'confirmed'
    appointment.save()
    return redirect('appointment_list')

def Reject_Appointment(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    appointment = Appointment.objects.get(id=pid)
    appointment.status = 'rejected'
    appointment.save()
    return redirect('appointment_list')

def Add_Appointment(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    doctor1 = Doctor.objects.all()
    patient1 = Patient.objects.all()
    if request.method == 'POST':
        d = request.POST['doctor']
        p = request.POST['patient']
        d1 = request.POST['date']
        t1= request.POST['time']
        doctor = Doctor.objects.filter(name=d).first()
        patient = Patient.objects.filter(name=p).first()

        try:
            Appointment.objects.create(doctor=doctor,patient=patient,date1=d1,time1=t1)
            error = "no"
        except:
            error = "yes"
    d = {'doctor':doctor1,'patient':patient1, 'error': error}
    return render(request, 'add_appointment.html', d)

def Delete_Appointment(request,pid):
    if not request.user.is_staff:
        return redirect('login')
    appointment = Appointment.objects.get(id=pid)
    appointment.delete()
    return redirect('appointment_list')

def View_Tests(request):
    if not request.user.is_staff:
        return redirect('login')
    tests = MedicalTest.objects.filter(is_active=True)
    d = {'tests': tests}
    return render(request, 'view_tests.html', d)

def Add_Test(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        n = request.POST['name']
        d = request.POST['description']
        p = request.POST['price']
        du = request.POST['duration']
        pr = request.POST['preparation']
        try:
            MedicalTest.objects.create(name=n, description=d, price=p, duration=du, preparation=pr)
            error = "no"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'add_test.html', d)

def Delete_Test(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    test = MedicalTest.objects.get(id=pid)
    test.delete()
    return redirect('view_tests')

def View_Test_Bookings(request):
    if not request.user.is_staff:
        return redirect('login')
    bookings = TestBooking.objects.all().order_by('-date', '-time')
    d = {'bookings': bookings}
    return render(request, 'view_test_bookings.html', d)

def Accept_Test_Booking(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    booking = TestBooking.objects.get(id=pid)
    booking.status = 'confirmed'
    booking.save()
    return redirect('view_test_bookings')

def Reject_Test_Booking(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    booking = TestBooking.objects.get(id=pid)
    booking.status = 'cancelled'
    booking.save()
    return redirect('view_test_bookings')

def home(request):
    doctor_count = Doctor.objects.count()
    patient_count = Patient.objects.count()
    appointment_count = Appointment.objects.count()
    test_booking_count = TestBooking.objects.count()
    
    # Get recent test bookings
    test_bookings = TestBooking.objects.select_related('patient', 'test').order_by('-date', '-time')[:10]
    
    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'appointment_count': appointment_count,
        'test_booking_count': test_booking_count,
        'test_bookings': test_bookings,
    }
    return render(request, 'home.html', context)

@login_required
def upload_test_result(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id)
    
    if request.method == 'POST':
        if request.FILES.get('result_pdf'):
            booking.result_pdf = request.FILES['result_pdf']
            booking.status = 'completed'
            booking.result_uploaded_at = timezone.now()
            booking.save()
            messages.success(request, 'Test result uploaded successfully.')
            return redirect('view_test_bookings')
    
    return render(request, 'upload_test_result.html', {
        'booking': booking
    })

@login_required(login_url='login')
def medicine_list(request):
    medicines = Medicine.objects.filter(expiry_date__gte=timezone.now().date())
    return render(request, 'medicine_list.html', {'medicines': medicines})

@login_required(login_url='login')
def medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    return render(request, 'medicine_detail.html', {'medicine': medicine})

@login_required(login_url='login')
def order_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        payment_method = request.POST.get('payment_method', 'bkash')
        if quantity <= medicine.quantity:
            total_price = medicine.price * quantity
            order = MedicineOrder.objects.create(
                user=request.user,
                medicine=medicine,
                quantity=quantity,
                total_price=total_price,
                payment_method=payment_method
            )
            medicine.quantity -= quantity
            medicine.save()
            # Create Payment record
            payment = Payment.objects.create(
                user=request.user,
                payment_type='medicine',
                related_id=order.id,
                method=payment_method,
                amount=total_price,
                status='pending'
            )
            return redirect('payment_interface', payment_id=payment.id)
        else:
            messages.error(request, 'Not enough stock available!')
    return render(request, 'order_medicine.html', {'medicine': medicine})

@login_required(login_url='login')
def medicine_orders(request):
    orders = MedicineOrder.objects.filter(user=request.user)
    return render(request, 'medicine_orders.html', {'orders': orders})

@login_required(login_url='admin_login')
def admin_medicine_list(request):
    if not request.user.is_superuser:
        return redirect('login')
    medicines = Medicine.objects.all()
    today = timezone.now().date()
    
    # Calculate counts
    low_stock_count = Medicine.objects.filter(quantity__lte=10).count()
    expired_count = Medicine.objects.filter(expiry_date__lt=today).count()
    pending_orders_count = MedicineOrder.objects.filter(status='pending').count()

    context = {
        'medicines': medicines,
        'today': today,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'pending_orders_count': pending_orders_count
    }
    return render(request, 'admin_medicine_list.html', context)

@login_required(login_url='admin_login')
def admin_expired_medicines(request):
    if not request.user.is_superuser:
        return redirect('login')
    medicines = Medicine.objects.filter(expiry_date__lt=timezone.now().date())
    return render(request, 'admin_expired_medicines.html', {'medicines': medicines, 'today': timezone.now().date()})

@login_required(login_url='admin_login')
def admin_add_medicine(request):
    if not request.user.is_superuser:
        return redirect('login')
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'admin_add_medicine.html', {'form': form})

@login_required(login_url='admin_login')
def admin_edit_medicine(request, medicine_id):
    if not request.user.is_superuser:
        return redirect('login')
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('admin_medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'admin_edit_medicine.html', {'form': form, 'medicine': medicine})

@login_required(login_url='admin_login')
def admin_delete_medicine(request, medicine_id):
    if not request.user.is_superuser:
        return redirect('login')
    medicine = get_object_or_404(Medicine, id=medicine_id)
    medicine.delete()
    messages.success(request, 'Medicine deleted successfully!')
    return redirect('admin_medicine_list')

@login_required(login_url='admin_login')
def admin_medicine_orders(request):
    if not request.user.is_superuser:
        return redirect('login')
    orders = MedicineOrder.objects.all()
    return render(request, 'admin_medicine_orders.html', {'orders': orders})

@login_required(login_url='admin_login')
def update_order_status(request, order_id):
    if not request.user.is_superuser:
        return redirect('login')
    order = get_object_or_404(MedicineOrder, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        messages.success(request, 'Order status updated successfully!')
    return redirect('admin_medicine_orders')

@login_required(login_url='admin_login')
def admin_low_stock_medicines(request):
    if not request.user.is_superuser:
        return redirect('login')
    medicines = Medicine.objects.filter(quantity__lte=10)
    return render(request, 'admin_low_stock_medicines.html', {'medicines': medicines})

@login_required(login_url='login')
def payment_interface(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    show_bkash_pin = False
    bkash_number = None

    # Always reset to number input on GET for bKash
    if payment.method == 'bkash' and request.method == 'GET':
        if 'bkash_number' in request.session:
            del request.session['bkash_number']

    if request.method == 'POST':
        if payment.method == 'bkash':
            # Handle back button
            if 'bkash_back' in request.POST:
                if 'bkash_number' in request.session:
                    del request.session['bkash_number']
                show_bkash_pin = False
                bkash_number = None
            # Step 1: User submits number only
            elif 'bkash_number' in request.POST and 'bkash_pin' not in request.POST:
                bkash_number = request.POST.get('bkash_number')
                if not bkash_number or not bkash_number.startswith('01') or len(bkash_number) != 11:
                    messages.error(request, 'Please enter a valid bKash number.')
                else:
                    request.session['bkash_number'] = bkash_number
                    show_bkash_pin = True
            # Step 2: User submits PIN
            elif 'bkash_pin' in request.POST:
                bkash_number = request.session.get('bkash_number')
                bkash_pin = request.POST.get('bkash_pin')
                if not bkash_number or not bkash_pin:
                    messages.error(request, 'Please enter both bKash number and PIN.')
                    show_bkash_pin = not not bkash_number
                else:
                    try:
                        gateway = get_payment_gateway('bkash')
                        customer_info = {'number': bkash_number, 'pin': bkash_pin}
                        result = gateway.process_payment(
                            amount=payment.amount,
                            reference_id=f"PAY-{payment.id}",
                            customer_info=customer_info
                        )
                        if result.get('status') == 'success':
                            payment.status = 'completed'
                            payment.save()
                            # Update related order status
                            if payment.payment_type == 'medicine':
                                order = MedicineOrder.objects.get(id=payment.related_id)
                                order.payment_status = 'done'
                                order.status = 'completed'
                                order.save()
                            elif payment.payment_type == 'appointment':
                                appointment = Appointment.objects.get(id=payment.related_id)
                                appointment.status = 'confirmed'
                                appointment.save()
                            elif payment.payment_type == 'test':
                                booking = TestBooking.objects.get(id=payment.related_id)
                                booking.status = 'confirmed'
                                booking.save()
                            # Send email notifications
                            subject = 'Payment Confirmation - Hospital Management System'
                            message = f"Dear {request.user.username},\n\nYour payment of ${payment.amount} for {payment.payment_type} has been received and confirmed.\n\nThank you!"
                            send_mail(subject, message, 'admin@hospital.com', [request.user.email])
                            # Notify admin
                            admin_email = 'admin@hospital.com'
                            admin_message = f"Payment received from {request.user.username} (${payment.amount}) for {payment.payment_type}."
                            send_mail('New Payment Received', admin_message, 'admin@hospital.com', [admin_email])
                            messages.success(request, 'Payment successful!')
                            # Clean up session
                            if 'bkash_number' in request.session:
                                del request.session['bkash_number']
                            return redirect('user_dashboard')
                        else:
                            payment.status = 'failed'
                            payment.save()
                            messages.error(request, f'Payment failed: {result.get("message", "Unknown error")}')
                            show_bkash_pin = True
                    except Exception as e:
                        payment.status = 'failed'
                        payment.save()
                        messages.error(request, f'Payment failed: {str(e)}')
                        show_bkash_pin = True
        else:
            # Other payment methods (original logic)
            try:
                gateway = get_payment_gateway(payment.method)
                customer_info = {}
                if payment.method == 'rocket':
                    customer_info = {
                        'number': request.POST.get('rocket_number'),
                        'pin': request.POST.get('rocket_pin')
                    }
                elif payment.method == 'dbbl':
                    customer_info = {
                        'account_number': request.POST.get('dbbl_number'),
                        'pin': request.POST.get('dbbl_pin')
                    }
                elif payment.method in ['visa', 'mastercard']:
                    customer_info = {
                        'card': {
                            'number': request.POST.get('card_number'),
                            'expiry': request.POST.get('expiry_date'),
                            'cvv': request.POST.get('cvv'),
                            'name': request.POST.get('card_name')
                        }
                    }
                result = gateway.process_payment(
                    amount=payment.amount,
                    reference_id=f"PAY-{payment.id}",
                    customer_info=customer_info
                )
                if result.get('status') == 'success':
                    payment.status = 'completed'
                    payment.save()
                    if payment.payment_type == 'medicine':
                        order = MedicineOrder.objects.get(id=payment.related_id)
                        order.payment_status = 'done'
                        order.status = 'completed'
                        order.save()
                    elif payment.payment_type == 'appointment':
                        appointment = Appointment.objects.get(id=payment.related_id)
                        appointment.status = 'confirmed'
                        appointment.save()
                    elif payment.payment_type == 'test':
                        booking = TestBooking.objects.get(id=payment.related_id)
                        booking.status = 'confirmed'
                        booking.save()
                    subject = 'Payment Confirmation - Hospital Management System'
                    message = f"Dear {request.user.username},\n\nYour payment of ${payment.amount} for {payment.payment_type} has been received and confirmed.\n\nThank you!"
                    send_mail(subject, message, 'admin@hospital.com', [request.user.email])
                    admin_email = 'admin@hospital.com'
                    admin_message = f"Payment received from {request.user.username} (${payment.amount}) for {payment.payment_type}."
                    send_mail('New Payment Received', admin_message, 'admin@hospital.com', [admin_email])
                    messages.success(request, 'Payment successful!')
                    if payment.payment_type == 'medicine':
                        return redirect('medicine_orders')
                    elif payment.payment_type == 'appointment':
                        return redirect('user_dashboard')
                    elif payment.payment_type == 'test':
                        return redirect('my_test_bookings')
                    else:
                        return redirect('user_dashboard')
                else:
                    payment.status = 'failed'
                    payment.save()
                    messages.error(request, f'Payment failed: {result.get("message", "Unknown error")}' )
                    return redirect('payment_interface', payment_id=payment.id)
            except Exception as e:
                payment.status = 'failed'
                payment.save()
                messages.error(request, f'Payment failed: {str(e)}')
                return redirect('payment_interface', payment_id=payment.id)

    # For GET or after POST, render the template with the right context
    if payment.method == 'bkash':
        if not show_bkash_pin and not bkash_number:
            bkash_number = request.session.get('bkash_number')
            if bkash_number:
                show_bkash_pin = True
    return render(request, 'payment_interface.html', {
        'payment': payment,
        'show_bkash_pin': show_bkash_pin,
        'bkash_number': bkash_number
    })

@login_required(login_url='admin_login')
def admin_payment_history(request):
    if not request.user.is_superuser:
        return redirect('login')
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'admin/payment_history.html', {'payments': payments})

def verify_email(request):
    import time
    from django.contrib.auth.models import User
    if 'pending_registration' not in request.session:
        messages.error(request, 'No registration in progress.')
        return redirect('register')
    reg = request.session['pending_registration']
    if request.method == 'POST':
        code = request.POST.get('code')
        now = time.time()
        if now - reg['timestamp'] > 300:
            del request.session['pending_registration']
            messages.error(request, 'Verification code expired. Please register again.')
            return redirect('register')
        if code == reg['code']:
            user = User.objects.create_user(
                username=reg['username'],
                email=reg['email'],
                password=reg['password'],
                first_name=reg['first_name'],
                last_name=reg['last_name']
            )
            user.save()
            # Save phone and gender to UserProfile if model exists
            try:
                from .models import UserProfile
                UserProfile.objects.create(user=user, phone_number=reg['phone'], gender=reg['gender'])
            except Exception:
                pass
            del request.session['pending_registration']
            messages.success(request, 'Email verified! Registration successful. Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification code.')
    return render(request, 'verify_email.html')

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # Update user info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile info
        profile.phone_number = request.POST.get('phone', profile.phone_number)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.location = request.POST.get('location', profile.location)
        profile.coordinates = request.POST.get('coordinates', profile.coordinates)

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('user_dashboard')

    context = {
        'user': user,
        'profile': profile,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='login')
def low_stock_medicines(request):
    medicines = Medicine.objects.filter(quantity__lte=10, expiry_date__gte=timezone.now().date())
    return render(request, 'medicine_list.html', {'medicines': medicines, 'low_stock': True})

@login_required(login_url='login')
def delete_medicine(request, medicine_id):
    if not request.user.is_staff:
        return redirect('medicine_list')
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicine_list')
    return redirect('medicine_list')

def Edit_Doctor(request, doctor_id):
    if not request.user.is_staff:
        return redirect('login')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    error = ""
    if request.method == 'POST':
        doctor.name = request.POST['name']
        doctor.mobile = request.POST['contact']
        doctor.special = request.POST['special']
        doctor.experience = request.POST.get('experience', doctor.experience)
        doctor.consultation_fee = request.POST.get('consultation_fee', doctor.consultation_fee)
        doctor.available_days = request.POST.get('available_days', doctor.available_days)
        doctor.available_time = request.POST.get('available_time', doctor.available_time)
        if 'profile_picture' in request.FILES:
            doctor.profile_picture = request.FILES['profile_picture']
        doctor.save()
        error = "no"
        return redirect('doctor_list')
    return render(request, 'edit_doctor.html', {'doctor': doctor, 'error': error})

@login_required(login_url='admin_login')
def accept_medicine_order(request, order_id):
    if not request.user.is_staff:
        return redirect('login')
    from .models import MedicineOrder
    order = get_object_or_404(MedicineOrder, id=order_id)
    if order.status == 'pending' and order.payment_status == 'done':
        order.status = 'completed'
        order.save()
        messages.success(request, 'Order accepted successfully!')
    else:
        messages.error(request, 'Cannot accept order. Payment not completed or order is not pending.')
    return redirect('admin_medicine_orders')

def test_maps_key(request):
    if request.user.is_superuser:  # Only allow superusers to see the key
        return JsonResponse({
            'key_configured': bool(settings.GOOGLE_MAPS_API_KEY),
            'key_length': len(settings.GOOGLE_MAPS_API_KEY) if settings.GOOGLE_MAPS_API_KEY else 0
        })
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@login_required(login_url='admin_login')
def edit_test(request, test_id):
    if not request.user.is_staff:
        return redirect('login')
    
    test = get_object_or_404(MedicalTest, id=test_id)
    
    if request.method == 'POST':
        test.name = request.POST.get('name')
        test.description = request.POST.get('description')
        test.price = request.POST.get('price')
        test.duration = request.POST.get('duration')
        test.preparation = request.POST.get('preparation')
        test.is_active = request.POST.get('is_active', False) == 'on'
        
        try:
            test.save()
            messages.success(request, 'Test updated successfully!')
            return redirect('view_tests')
        except Exception as e:
            messages.error(request, f'Error updating test: {str(e)}')
    
    return render(request, 'edit_test.html', {'test': test})