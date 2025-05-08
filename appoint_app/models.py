from django.db import models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator
from django.utils import timezone
import random
import string
from account.models import User
from django.utils import timezone
import random
import string
from account.models import Patient


CENTRE_CHOICES =[
  
        ('Kakdwip','Kakdwip'),
        ('5_No_Hat','5 No. Hat'),
        #('Janakalyan_Sangha','Janakalyan Sangha'),
        #('Bharat_Sevasram','Bharat Sevasram',),
        
        
    ]

DAY_CHOICES =[
   
    (0,'Monday'),
    (1,'Tuesday'),
    (2,'Wednessday'),
    (3,'Thursday'),
    (4,'Friday'),
    (5,'Saturday'),
    (6,'Sunday'),
]

class Slot(models.Model):     
    date = models.DateField(validators=[MinValueValidator(datetime.date.today)],blank=False, null=False)
    centre = models.CharField('Centre', choices=CENTRE_CHOICES,blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    allowed = models.PositiveIntegerField(blank=False, null=False)
    booked = models.PositiveIntegerField(default=0,blank=False,null=False)


    def __str__(self):     
        return f"{self.date.day}-{self.date.month}-{self.date.year} ({self.centre})" 
    
    def update_booked(self):
        self.booked = Appointment.objects.filter(slot=self, appoint_status= 'Scheduled').count()
        self.save(update_fields=["booked"])



  



# Create a method to generate a random appointment ID
def generate_appointment_id():
    alphanumeric = string.ascii_letters + string.digits
    return ''.join(random.choices(alphanumeric, k=6))





# Create a model for Appointment
class Appointment(models.Model): 
    APPOINTMENT_STATUS_CHOICES = (
        ('', '-----'),
        ('Failed', 'Failed'),
        ('Scheduled', 'Scheduled'),
        ('Canceled', 'Canceled'),
        ('Completed', 'Completed'),        
    )

    PAYMENT_CHOICES = [
    (True, 'Verified'),
    (False, 'N/A'),]
    
    payment = models.BooleanField('Payment', default=False, blank=True, null=True, choices=PAYMENT_CHOICES)
    appoint_id = models.CharField('Appointment ID', primary_key=True, max_length=6, default=generate_appointment_id, editable=False)
    appointee = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='Patients', blank=False)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='Slot', blank=False)
    book_time = models.DateTimeField('Booked on', default=timezone.now, editable=False)
    approve_date = models.DateTimeField('Approved on', blank=True, null=True)
    doctor_remarks = models.CharField('Remarks', max_length=100, blank=True, null=True)
    appoint_status = models.CharField('Status', max_length=10, choices=APPOINTMENT_STATUS_CHOICES, blank=False)
    queue = models.PositiveIntegerField('Queue',editable=False,blank=True, null=True)

    def set_queue(self):
        max_value = Appointment.objects.filter(slot=self.slot).aggregate(models.Max('queue'))['queue__max']
        if max_value:
            return (max_value + 1)
        else:
            return 1
    
    def __str__(self):

        if self.appoint_status == 'Scheduled':            
            if self.slot.date < datetime.date.today():
                self.appoint_status = 'Completed'
                self.save(update_fields=["appoint_status"])
     
        return self.appoint_id
    

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.slot.update_booked()


    def save(self, *args, **kwargs):
        
        flag = False
        if self._state.adding:
            if self.appoint_status =='Scheduled':
                self.queue = self.set_queue()
            
        else:
            old = Appointment.objects.get(pk=self.pk)
            if self.slot != old.slot:
                flag = True
                if self.appoint_status == 'Scheduled':
                    self.queue = self.set_queue()
                else:
                    self.queue = None
            elif self.appoint_status == 'Scheduled' and not self.queue:
                self.queue = self.set_queue()

        super().save(*args, **kwargs)
        
        if flag:
            old.slot.update_booked()
        self.slot.update_booked()
        
 
       


class Schedule(models.Model):     
    centre = models.CharField(max_length=50,choices=CENTRE_CHOICES)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES, blank=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    allowed = models.PositiveIntegerField(blank=False, null=False)

class Misc(models.Model):
    date = models.DateTimeField(auto_now_add=True,null=True)
    from_date = models.DateField(blank=False, null=False)
    to_date = models.DateField(blank=False, null=False)