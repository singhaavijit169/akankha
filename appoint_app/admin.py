from django.contrib import admin
from .models import Appointment, User,Slot, Schedule
admin.site.disable_action('delete_selected')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appoint_id', 'appointee','slot__date', 'slot__centre','book_time','appoint_status','queue')
    ordering = ('book_time',)
    list_filter = ('appoint_id', 'appointee', 'appoint_status', 'slot__date', 'slot__centre','slot', 'book_time', 'approve_date') 
    list_per_page = 10
    list_per_page = 500

    

   
    

    

@admin.register(Slot)
class Slot(admin.ModelAdmin):
    list_display = ('date','centre', 'start_time', 'end_time', 'allowed','booked')
    list_filter = ( 'date','centre')
    readonly_fields = ('booked',)
    list_per_page = 10
    ordering = ('-date',)

@admin.register(Schedule)
class Schedule(admin.ModelAdmin):
    list_display = ('day','centre', 'start_time', 'end_time', 'allowed')
    list_filter = ( 'centre','day')

    list_per_page = 10
    ordering = ('day',)
    list_per_page = 10