from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import random
import string
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
import datetime

GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]  

# Create a Custom User Model   
class User(AbstractUser):

    profile_photo = models.ImageField(upload_to='Profile-photos/', null=True, blank=True)
    active = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='Profile-photos/', null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = PhoneNumberField(max_length=13, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email_verified = models.BooleanField(default=False,blank=True, null=True)
    
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)

    def set_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def set_last_logout(self):
        self.last_logout = timezone.now()
        self.save(update_fields=['last_logout'])


class Patient(models.Model):
    first_name = models.CharField('First Name',max_length=50,blank=False )
    last_name = models.CharField(max_length=50,blank=False,)
    dob = models.DateField('Date of Birth',validators=[MaxValueValidator(datetime.date.today)],blank=True,null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6,blank=True,null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='User',blank=False)
    def __str__(self):     
        return f"{self.first_name} {self.last_name}"




# Create a model for OTP(One Time Password)    
class OTP(models.Model):
    otp_code = models.CharField(max_length=6)
    otp_created = models.DateTimeField(default=timezone.now)
    otp_verified = models.BooleanField(default=False)
    for_email = models.EmailField(null=True, blank=True, default="")

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices('0123456789', k=6))
    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"




