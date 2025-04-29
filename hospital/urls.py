from django.urls import path
from . import views
from .user_views import *
from hospital.admin import admin_site
urlpatterns = [
    # Medicine Management URLs
    path('staff/medicines/', views.admin_medicine_list, name='admin_medicine_list'),
    path('staff/medicines/add/', views.admin_add_medicine, name='admin_add_medicine'),
    path('staff/medicines/<int:medicine_id>/edit/', views.admin_edit_medicine, name='admin_edit_medicine'),
    path('staff/medicines/<int:medicine_id>/delete/', views.admin_delete_medicine, name='admin_delete_medicine'),
    path('staff/medicine-orders/', views.admin_medicine_orders, name='admin_medicine_orders'),
    path('staff/medicine-orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('staff/medicine-orders/<int:order_id>/accept/', views.accept_medicine_order, name='accept_medicine_order'),
    path('staff/medicines/low-stock/', views.admin_low_stock_medicines, name='admin_low_stock_medicines'),
    path('staff/medicines/expired/', views.admin_expired_medicines, name='admin_expired_medicines'),
    path('staff/payments/', views.admin_payment_history, name='admin_payment_history'),

    # Admin Panel URLs
    path('admin/', admin_site.urls),
    path('', views.Index, name='home'),
    path('about/', views.About, name='about'),
    path('contact/', views.Contact, name='contact'),
    path('admin_login/', views.Login, name='admin_login'),
    path('logout/', views.Logout, name='logout'),
    
    # Authentication URLs
    path('login/', views.UserLogin, name='login'),
    path('register/', views.Register, name='register'),
    
    # Doctor URLs
    path('doctor/list/', views.View_Doctor, name='doctor_list'),
    path('doctor/add/', views.Add_Doctor, name='add_doctor'),
    path('doctor/delete/<int:pid>/', views.Delete_Doctor, name='delete_doctor'),
    path('doctor/edit/<int:doctor_id>/', views.Edit_Doctor, name='edit_doctor'),
    
    # Patient URLs
    path('patient/list/', views.View_Patient, name='patient_list'),
    path('patient/add/', views.Add_Patient, name='add_patient'),
    path('patient/delete/<int:pid>/', views.Delete_Patient, name='delete_patient'),
    
    # Appointment URLs
    path('appointment/list/', views.View_Appointment, name='appointment_list'),
    path('appointment/add/', views.Add_Appointment, name='add_appointment'),
    path('appointment/delete/<int:pid>/', views.Delete_Appointment, name='delete_appointment'),
    path('appointment/accept/<int:pid>/', views.Accept_Appointment, name='accept_appointment'),
    path('appointment/reject/<int:pid>/', views.Reject_Appointment, name='reject_appointment'),
    
    # Test URLs
    path('test/list/', views.View_Tests, name='test_list'),
    path('test/add/', views.Add_Test, name='add_test'),
    path('test/<int:test_id>/edit/', views.edit_test, name='edit_test'),
    path('test/delete/<int:pid>/', views.Delete_Test, name='delete_test'),
    path('test/bookings/', views.View_Test_Bookings, name='view_test_bookings'),
    path('test/booking/accept/<int:pid>/', views.Accept_Test_Booking, name='accept_test_booking'),
    path('test/booking/reject/<int:pid>/', views.Reject_Test_Booking, name='reject_test_booking'),
    path('test/booking/upload-result/<int:booking_id>/', views.upload_test_result, name='upload_test_result'),
    
    # User Panel URLs
    path('user/register/', user_register, name='user_register'),
    path('user/login/', user_login, name='user_login'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('user/doctors/', doctor_list, name='doctor_list'),
    path('user/book-appointment/<int:doctor_id>/', book_appointment, name='book_appointment'),
    path('user/cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('user/tests/', test_list, name='test_list'),
    path('user/my-test-bookings/', my_test_bookings, name='my_test_bookings'),
    path('user/book-test/<int:test_id>/', book_test, name='book_test'),
    path('user/cancel-test/<int:booking_id>/', cancel_test, name='cancel_test'),
    path('user/payments/', user_payment_history, name='user_payment_history'),
    
    # Medicine URLs
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:medicine_id>/order/', views.order_medicine, name='order_medicine'),
    path('medicine-orders/', views.medicine_orders, name='medicine_orders'),
    path('medicines/low-stock/', views.low_stock_medicines, name='low_stock_medicines'),
    path('medicines/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),

    path('payment/<int:payment_id>/', views.payment_interface, name='payment_interface'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('test-maps-key/', views.test_maps_key, name='test_maps_key'),
] 