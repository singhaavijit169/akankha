from django.contrib import admin
from .models import Payment
from django.utils import timezone

# Create a class to display the Payment model in the Admin interface
class PaymentAdmin(admin.ModelAdmin):
    def date(self, obj):
        if obj.date_created:
            return timezone.localtime(obj.date_created)
        return None

    list_display = ( 'order_id','amount',  'date_created',  'appointment','user',  'verified')
    list_filter = ( 'order_id','amount',  'date_created',  'appointment','user',  'verified')
    list_per_page = 500
admin.site.register(Payment, PaymentAdmin)
    
