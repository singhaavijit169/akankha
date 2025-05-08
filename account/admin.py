from django.contrib import admin
from .models import OTP, User, Patient
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
admin.site.unregister(Group)



# Create a custom user admin class
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'date_joined','last_login', 'last_logout', 'active',)
    list_filter = ( 'username',  'first_name', 'last_name', 'email', 'phone_number','date_joined', 'active','last_login', 'last_logout',)
    ordering = ('date_joined',)
    
    actions = ['deactivate_users', 'activate_users']
    # Custom actions
    def deactivate_users(self, request, queryset):
        queryset.update(active=False)
    deactivate_users.short_description = "Deactivate selected users"
    
    def activate_users(self, request, queryset):
        queryset.update(active=True)
    activate_users.short_description = "Activate selected users"
    
admin.site.register(User, CustomUserAdmin)


# Register models

    
    

class OTPAdmin(admin.ModelAdmin):
    list_display = ('otp_code', 'otp_created', 'otp_verified', 'for_email')
    list_filter = ('otp_code', 'otp_verified', 'otp_created', 'for_email',)
    readonly_fields = ('otp_code',  'otp_created', 'otp_verified', 'for_email')
    list_per_page = 10
     
admin.site.register(OTP, OTPAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'dob', 'phone_number','user')
    list_filter = ('first_name', 'last_name', 'gender', 'phone_number','user')
    list_per_page = 10
     
admin.site.register(Patient, PatientAdmin)





 


