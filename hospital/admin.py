from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from .models import Doctor, Patient, Appointment, UserProfile, MedicalTest, TestBooking, Medicine
from django.utils import timezone

class HospitalAdminSite(admin.AdminSite):
    site_header = 'Hospital Management System'
    site_title = 'Hospital Admin'
    index_title = 'Hospital Administration'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-dashboard/', self.test_dashboard_view, name='test-dashboard'),
            path('medicines/low-stock/', self.admin_view(self.low_stock_medicines_view), name='low_stock_medicines'),
        ]
        return custom_urls + urls

    def test_dashboard_view(self, request):
        # Get test statistics
        total_tests = MedicalTest.objects.count()
        active_tests = MedicalTest.objects.filter(is_active=True).count()
        total_bookings = TestBooking.objects.count()
        pending_bookings = TestBooking.objects.filter(status='pending').count()
        confirmed_bookings = TestBooking.objects.filter(status='confirmed').count()
        completed_bookings = TestBooking.objects.filter(status='completed').count()
        cancelled_bookings = TestBooking.objects.filter(status='cancelled').count()

        # Get recent bookings
        recent_bookings = TestBooking.objects.select_related('patient', 'test').order_by('-created_at')[:5]

        # Get popular tests
        popular_tests = MedicalTest.objects.annotate(
            booking_count=Count('testbooking')
        ).order_by('-booking_count')[:5]

        # Medicine statistics
        total_medicines = Medicine.objects.count()
        low_stock_medicines = Medicine.objects.filter(quantity__lte=10).count()
        expired_medicines = Medicine.objects.filter(expiry_date__lt=timezone.now().date()).count()

        context = {
            'total_tests': total_tests,
            'active_tests': active_tests,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'recent_bookings': recent_bookings,
            'popular_tests': popular_tests,
            'total_medicines': total_medicines,
            'low_stock_medicines': low_stock_medicines,
            'expired_medicines': expired_medicines,
            'title': 'Test Management Dashboard',
            'site_title': self.site_title,
            'site_header': self.site_header,
            'has_permission': True,
            'is_nav_sidebar_enabled': True,
            'available_apps': self.get_app_list(request),
        }
        return render(request, 'admin/test_dashboard.html', context)

    def low_stock_medicines_view(self, request):
        low_stock_medicines = Medicine.objects.filter(quantity__lte=10)
        context = dict(
            self.each_context(request),
            low_stock_medicines=low_stock_medicines,
            title='Low Stock Medicines',
        )
        return render(request, 'admin/low_stock_medicines.html', context)

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Add Test Management section
        test_management = {
            'name': 'Test Management',
            'app_label': 'test_management',
            'app_url': '/admin/test-dashboard/',
            'has_module_perms': True,
            'models': [
                {
                    'name': 'Test Dashboard',
                    'object_name': 'TestDashboard',
                    'admin_url': '/admin/test-dashboard/',
                    'view_only': True,
                },
                {
                    'name': 'Medical Tests',
                    'object_name': 'MedicalTest',
                    'admin_url': '/admin/hospital/medicaltest/',
                    'view_only': False,
                },
                {
                    'name': 'Test Bookings',
                    'object_name': 'TestBooking',
                    'admin_url': '/admin/hospital/testbooking/',
                    'view_only': False,
                },
            ],
        }
        # Add Low Stock Medicines link under Medicines
        for app in app_list:
            if app['name'] == 'Medicines' or app['app_label'] == 'hospital':
                app['models'].append({
                    'name': 'Low Stock Medicines',
                    'object_name': 'LowStockMedicines',
                    'admin_url': '/admin/medicines/low-stock/',
                    'view_only': True,
                })
        app_list.append(test_management)
        return app_list

# Create the admin site instance
admin_site = HospitalAdminSite(name='hospital_admin')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'date1', 'time1', 'status', 'symptoms', 'created_at')
    list_filter = ('status', 'date1', 'doctor', 'created_at')
    search_fields = ('patient__name', 'doctor__name', 'symptoms')
    readonly_fields = ('created_at',)
    actions = ['accept_appointments', 'reject_appointments', 'mark_as_cancelled']
    ordering = ('-created_at',)

    def accept_appointments(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{updated} appointment(s) have been accepted.")
    accept_appointments.short_description = "Accept selected pending appointments"

    def reject_appointments(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"{updated} appointment(s) have been rejected.")
    reject_appointments.short_description = "Reject selected pending appointments"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f"{updated} appointment(s) have been marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected appointments as cancelled"

@admin.register(MedicalTest)
class MedicalTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'is_active', 'get_booking_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

    def get_booking_count(self, obj):
        count = TestBooking.objects.filter(test=obj).count()
        return format_html('<span class="badge bg-info">{}</span>', count)
    get_booking_count.short_description = 'Total Bookings'

@admin.register(TestBooking)
class TestBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'test', 'date', 'time', 'status', 'get_notes', 'has_result', 'created_at')
    list_filter = ('status', 'date', 'test', 'created_at')
    search_fields = ('patient__name', 'test__name', 'notes')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    actions = ['accept_bookings', 'reject_bookings', 'mark_as_completed', 'mark_as_cancelled']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'test')
        }),
        ('Booking Details', {
            'fields': ('date', 'time', 'notes')
        }),
        ('Status Information', {
            'fields': ('status', 'created_at')
        }),
        ('Test Results', {
            'fields': ('result_pdf', 'result_uploaded_at'),
            'classes': ('collapse',),
            'description': 'Upload test results in PDF format'
        }),
    )

    def has_result(self, obj):
        return bool(obj.result_pdf)
    has_result.boolean = True
    has_result.short_description = 'Has Result'

    def get_notes(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    get_notes.short_description = 'Notes'

    def save_model(self, request, obj, form, change):
        if 'result_pdf' in form.changed_data:
            obj.result_uploaded_at = timezone.now()
        super().save_model(request, obj, form, change)

    def accept_bookings(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{updated} test booking(s) have been confirmed.")
    accept_bookings.short_description = "Accept selected pending bookings"

    def reject_bookings(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"{updated} test booking(s) have been rejected.")
    reject_bookings.short_description = "Reject selected pending bookings"

    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f"{updated} test booking(s) have been marked as completed.")
    mark_as_completed.short_description = "Mark selected bookings as completed"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f"{updated} test booking(s) have been cancelled.")
    mark_as_cancelled.short_description = "Cancel selected bookings"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# Register other models
admin_site.register(Doctor)
admin_site.register(Patient)
admin_site.register(UserProfile)