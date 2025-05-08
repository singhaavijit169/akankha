from datetime import time
from django import forms
from .models import User
from appoint_app.models import generate_appointment_id, Misc,Appointment
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from django.utils.safestring import mark_safe
from phonenumber_field.formfields import PhoneNumberField

from django.core.exceptions import ValidationError
from django.http import HttpResponse

GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    
RESOLVED_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]

DAY_CHOICES = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
    ]






# Create a custom password input widget with an eye icon to toggle password visibility
class PasswordInputWithToggle(PasswordInput):
    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer)
        eye_toggle = '''
        <div class="relative">
            {}
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5">
                <button 
                    type="button" 
                    class="text-blue-500 hover:text-gray-700 focus:outline-none focus:shadow-outline-blue active:text-gray-800 toggle-password">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        </div>
        '''.format(rendered)
        return mark_safe(eye_toggle)




# Create a custom Patient registration form
class PatientRegistrationForm(UserCreationForm):
   # patient_type = forms.ChoiceField(required=True, label='Patient Type', choices=PATIENT_TYPE_CHOICES, widget=forms.Select(attrs={'id': 'patient_type', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),)
  #  patient_id = forms.CharField(label='Patient ID', required=True, widget=forms.TextInput(attrs={'id': 'patient_id', 'autocomplete': '', 'placeholder': 'Enter your ID', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}), max_length=15)
    
    phone_number = PhoneNumberField(required=True, widget=forms.NumberInput(attrs={'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', 'id': 'phone_number','value':'+91 ', 'autocomplete': 'tel', 'placeholder': 'Enter your Phone Number'}))

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', 'id': 'email', 'autocomplete': 'email', 'placeholder': 'Enter your Email'}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'id': 'username', 'placeholder': 'Create your unique username', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}), required=True)
    password1 = forms.CharField(required=True, label='Password', widget=PasswordInputWithToggle(attrs={'id': 'password', 'autocomplete': 'current-password', 'placeholder': 'Create your password', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 pr-10'}))
    password2 = forms.CharField(required=True, label='Confirm Password', widget=PasswordInputWithToggle(attrs={'id': 'password2', 'autocomplete': 'new-password', 'placeholder': 'Confirm your password', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 pr-10'}))
    
    agree_to_terms = forms.BooleanField(
        label='Agree to Terms of Use & Privacy',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'id': 'agree_to_terms',
            'class': 'form-checkbox text-red h-9 w-9',
        }),
    )
    
    # Meta class to define the model and fields to be used in the form
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number',  'password1', 'password2', 'agree_to_terms']
    

 
    


    
 
    



# Create a custom form to update Profile (by Patients)
class UpdateProfileForm(forms.ModelForm):   
    profile_photo = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'hidden', 'accept': 'image/*',
        'id': 'profile_photo',
        'class': 'block w-full mt-2 mb-2 rounded-full border-0 border-none p-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent sm:text-sm'
    }))   
    first_name = forms.CharField(label='First Name:', required=True, widget=forms.TextInput(attrs={'id': 'first_name', 'autocomplete': '', 'placeholder': 'Enter your first name', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}), max_length=50)
    last_name = forms.CharField(label='Last Name:', required=True, widget=forms.TextInput(attrs={'id': 'last_name', 'autocomplete': '', 'placeholder': 'Enter your last name', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}), max_length=50)
    phone_number = PhoneNumberField(required=True, widget=forms.NumberInput(attrs={'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', 'id': 'phone_number','value':'+91 ', 'autocomplete': 'tel', 'placeholder': 'Enter your Phone Number'}))
    email = forms.EmailField(required=True, label='Email:', widget=forms.EmailInput(attrs={'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', 'id': 'email', 'autocomplete': 'email', 'placeholder': 'Update your Email'}))
    username = forms.CharField(label='Username:', widget=forms.TextInput(attrs={'id': 'username', 'placeholder': 'Create your unique username', 'required': True, 'class': 'block w-full rounded-full border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}), required=True)
    
    class Meta:
        model = User
        fields = ['profile_photo','username', 'first_name', 'last_name', 'email', 'phone_number']




class Create_auto_slot(forms.ModelForm):  
    from_date = forms.DateField()
    to_date = forms.DateField()
    
    class Meta:
        model = Misc
        fields = [ 'from_date','to_date']