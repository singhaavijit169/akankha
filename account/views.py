from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import get_template
from .forms import  PatientRegistrationForm,  UpdateProfileForm, Create_auto_slot
from account.models import Patient
from payments.models import Payment
from appoint_app.models import Slot,generate_appointment_id, Schedule, Misc, Appointment
from .models import  OTP,  User

import random
from io import BytesIO
from xhtml2pdf import pisa
from datetime import timedelta, date

#### Create a view to export an appointment's details (by Patient) to a PDF file
def export_appointment_pdf(request, appointment_id):
    appointment = get_object_or_404(Appointment, appoint_id=appointment_id)
    appointee = appointment.appointee
    payment = appointment.payment
    payment_display = "yes" if payment else "no"

    approved = appointment.approve_date if appointment.approve_date else "--"
    #scheduled_time = appointment.appoint_time if appointment.appoint_time else "--"
    scheduled_date = appointment.slot.date
    start_time = appointment.slot.start_time

    data = [
        {
            'appoint_id': appointment.appoint_id,
            'book_time': appointment.book_time,
            'centre': appointment.slot.centre,
            'patient': f"{appointee.first_name} {appointee.last_name}",
            'gender': appointee.gender,
            'phone_number': appointee.phone_number,
            #'email': appointee.email,
            'payment_display': payment_display,
            'approved': approved,
            'scheduled_date': scheduled_date,
            'start_time': start_time,
            'queue': appointment.queue,
            'appoint_status': appointment.appoint_status,
            'doctor_remarks': appointment.doctor_remarks,
        }
    ]

    template_path = 'appoint_app/appointment_report.html'
    context = {'data': data, 'user': request.user}
    #return render(request, 'appoint_app/appointment_report.html',{'data':data})
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return FileResponse(BytesIO(result.getvalue()), as_attachment=True, filename=f'Appointment_{appointment_id}_Report.pdf')
    else:
        return HttpResponse('Error Rendering PDF', status=400)
    


#### Create a view to export all Payments (by Admin) to a PDF file
def export_admin_all_payments_pdf(request):
    user_appointment = Payment.objects.all()
    data = []
    for payment in user_appointment:
        email_prefix = payment.email.split('@')[0] if payment.email else "--"
        patient = payment.appointment.appointee
        data.append([payment.receipt_number, "Rs." + str(payment.amount),  payment.date_created, patient, payment.appointment, payment.ref[:6] + '...' if len(payment.ref) > 6 else payment.ref, email_prefix])
    
    template_path = 'appoint_app/admin_all_payments_report.html'
    context = {'data': data}
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return FileResponse(BytesIO(result.getvalue()), as_attachment=True, filename='User Payments Report.pdf')
    else:
        return HttpResponse('Error Rendering PDF', status=400)


#### Create a view to export all Payments (by Patient) to a PDF file
def export_user_payments_pdf(request):
    user_payments = Payment.objects.filter(user=request.user)  # Fetch payments for the current user
    user = request.user
    data = []
    for payment in user_payments:
        verified_display = "yes" if payment.verified else "no"
        email_prefix = payment.email.split('@')[0] if payment.email else "--"
        data.append([payment.receipt_number, "Rs." + str(payment.amount), payment.date_created, payment.appointment, payment.ref[:6] + '...' if len(payment.ref) > 6 else payment.ref, verified_display, email_prefix])
    
    template_path = 'appoint_app/user_payments_report.html'
    context = {'user': user, 'data': data}
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return FileResponse(BytesIO(result.getvalue()), as_attachment=True, filename='User Payments Report.pdf')
    else:
        return HttpResponse('Error Rendering PDF', status=400)



#### Create a view to export all Appointments (by Admin) to a PDF file
def export_appointments_payments_pdf(request):
    appointments = Appointment.objects.all().order_by('-appoint_time')
    data = []
    for appointment in appointments:
        patient = appointment.appointee
        approved = appointment.approve_date if appointment.approve_date else "--"
        scheduled = appointment.appoint_time if appointment.appoint_time else "--"
        #closed = appointment.close_date if appointment.close_date else "--"
        #patient_type = "Student" if patient.is_Student_Patient else "Staff" if patient.is_Staff_Patient else "None"
        payment = Payment.objects.filter(appointment=appointment).first()
        payment_display = "Verified" if payment and payment.verified else "Failed"
        
        data.append([appointment.appoint_id, patient,  appointment.book_time, approved, scheduled,  appointment.appoint_status, payment_display])
    
    template_path = 'appoint_app/appointments_payments_report.html'
    context = {'data': data}
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return FileResponse(BytesIO(result.getvalue()), as_attachment=True, filename='All Appointments.pdf')
    else:
        return HttpResponse('Error Rendering PDF', status=400)
    

# Create a function to check if an email exists in the database
def check_email_exists(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})


# Create a function to toggle dark mode (settings)
def toggle_dark_mode(request):
    if request.method == "POST" and request.user.is_authenticated:
        dark_mode = request.POST.get("darkMode")
        # Save the user's preference for dark mode in the session or database
        request.session["dark_mode"] = dark_mode
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)     


# Create a method to generate a random 6-digit OTP
def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

  
# Create a view for user login
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.active:
                login(request, user)
                user.set_last_login()  # Update last login time
                try:
                    if user.is_superuser:
                        
                        otp = OTP.objects.create(otp_code=OTP.generate_otp(), for_email=user.email)
                        send_mail_otp(user.email, otp.otp_code)
                       
                        request.session['otp'] = otp.pk
                        return redirect('admin_otp_verification')  # Redirect to OTP verification page
                    
                    elif user.email_verified == True:
                        return redirect('patients_portal')
                    elif user.email_verified == False:
                        otp = OTP.objects.create(otp_code=OTP.generate_otp(), for_email=user.email)
                        send_mail_otp(user.email, otp.otp_code) 
                        request.session['otp'] = otp.pk
                        return redirect('reg_otp_verification')                      
                except Exception as e:
                    messages.error(request, "Oops! An error occurred. Check your internet connection.")
                    return redirect('login')
            else:
                # User account is inactive, prevent login
                messages.error(request, "Oops! Your account is currently deactivated.")
                return render(request, 'appoint_app/login.html')
        else:
            messages.error(request, 'Invalid Username or Password!')
            return redirect('login') 

    return render(request, "appoint_app/login.html")


# Function to send OTP to the user's email
def send_mail_otp(email, otp):
    try:
        subject = 'OTP Verification Code'
        message = f'Your OTP for login is: {otp}'
        email_from = settings.EMAIL_HOST_USER  # Use the default email address from settings
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        raise e




# OTP verification view for Admins
def admin_otp_verification(request):
    if request.method == 'POST':
        entered_otp = ''.join(request.POST.get(f'digit{i+1}') for i in range(6))  # Concatenate digits to form OTP
        otp_id = request.session.get('otp')
        if otp_id:
            otp = OTP.objects.get(pk=otp_id)
            if entered_otp == otp.otp_code:
                otp.otp_verified = True
                otp.save()
                del request.session['otp']  # Remove OTP from session after successful verification
                return redirect('admins_portal')  # Redirect to admin's dashboard
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                # Pass the error messages to the template context
                error_messages = messages.get_messages(request)
                return render(request, 'appoint_app/admin_otp_verification.html', {'error_messages': error_messages})
        else:
            # Handle case where there is no OTP stored in session
            return redirect('login')
    return render(request, 'appoint_app/admin_otp_verification.html')

def reg_otp_verification(request):
    if request.method == 'POST':
        entered_otp = ''.join(request.POST.get(f'digit{i+1}') for i in range(6))  # Concatenate digits to form OTP
        otp_id = request.session.get('otp')
        if otp_id:
            otp = OTP.objects.get(pk=otp_id)
            if entered_otp == otp.otp_code:
                otp.otp_verified = True
                otp.save()
                del request.session['otp']
                x = request.user  # Remove OTP from session after successful verification
                x.email_verified = True
                x.save()

                return redirect('patients_portal')  # Redirect to admin's dashboard
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                # Pass the error messages to the template context
                error_messages = messages.get_messages(request)
                return render(request, 'appoint_app/admin_otp_verification.html', {'error_messages': error_messages})
        else:
            # Handle case where there is no OTP stored in session
            return redirect('login')
    
    return render(request, 'appoint_app/admin_otp_verification.html')



# Create a view for account deletion confirmation
def delete_account_confirmation(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.delete()

            try:
                # Send email to the registered patient
                subject = 'Akankha Homeo - Account Deactivate'
                email_from = settings.EMAIL_HOST_USER
                message = f'Your account has been permanently deleted!\nWe are sad to see you go!\n\nThe Akankha Homeo™'
                send_mail(subject, message, email_from, [user.email])
            except Exception as e:
                messages.error(request, "Oops! An error occurred. Check your internet connection.")
                return redirect('delete_account_confirmation')  # Redirect back to confirmation page if email fails'''

            messages.error(request, 'Your account has been permanently deleted!')
            logout(request)  # Logout the user after deletion
            return redirect('login')  # Redirect to login or appropriate page
        except Exception as e:
            # Handle any exceptions that occur during account deletion
            messages.error(request, 'An error occurred while deleting your account! Please try again later.')
            return redirect('delete_account_confirmation')  # Redirect back to confirmation page if deletion fails
    else:
        # If the request method is not POST, display the confirmation page
        return render(request, "appoint_app/delete_account_confirmation.html")


# Create a view for user logout
def logout_user(request):
    logout(request)
    if request.user.is_authenticated:
        request.user.set_last_logout()  # Update last logout time
        messages.success(request, 'Logout Success!')
    return redirect('login')
    


def register_patient(request):
    
    if request.method == "POST":
        
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            
            try:
                user = form.save(commit=False)

                
                user.save()       

                try:
                    # Send email to the registered patient
                    subject = 'Akankha Homeo - Acoount Activation'
                    email_from = settings.EMAIL_HOST_USER
                    message = (f'Welcome to Akankha Homeo {user.username}!\n\nDear patient, you are one step away from booking your first Doctor Appointment.\n'
                               'That is not all! You can even request for a video call with your Doctor today!\nJoin thousands of Appoint Master users NOW!\n\n'
                               'Do LOG INTO YOUR ACCOUNT AND UPDATE YOUR PROFILE.\n\nThe Akankha Homeo™')
                    send_mail(subject, message, email_from, [user.email])
                except Exception as e:
                    messages.error(request, "Oops! An error occurred while sending the confirmation email. Check your internet connection.")
                    user.delete()  # Rollback user creation if email fails
                    return redirect('register_patient')

                messages.success(request, 'Your Account has been created successfully!')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred while creating your account. Please try again later.')
                return redirect('register_patient')
    else:
        form = PatientRegistrationForm()
    return render(request, "appoint_app/register_patient.html", {'form': form})



#
def create_appointment_patient(request):
    if request.method == 'POST':
        try:
            centre = request.POST['centre']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            dob = request.POST['dob']
            phone_number = request.POST['phone']
            gender = request.POST['gender']
            id = request.POST['patient_name']
            if ( id == 'new'):

                instance = Patient(first_name=first_name, last_name=last_name, dob=dob, phone_number=phone_number, gender=gender,user=request.user)
                instance.save()
            else:
                instance=get_object_or_404(Patient,id=id)
                instance.first_name = first_name
                instance.last_name = last_name
                instance.dob = dob
                instance.phone_number = phone_number
                instance.gender = gender

            instance.save()    
            slot_list = Slot.objects.filter(centre=centre, date__gt=timezone.now().date()).all()
            for i in slot_list:
                if i.allowed > i.booked:
                    i.vacent = i.allowed - i.booked
                else:
                    i.vacent = 0
            return render(request,'appoint_app/book-slot-patient.html',{'slot_list': slot_list,'centre':centre,'patient':instance})
        except:
            messages.error(request, 'OOps! Something went wrong Please try again later.')
            return redirect('create-appointment-patient')  # Redirect back to confirmation page if deletion fails       
        
    patient = Patient.objects.filter(user=request.user)
    return render(request, "appoint_app/create_appointment_patient.html",{'patient': patient})

    
def book_slot_patient(request):   
    if request.method == 'POST':
        slot_id = request.POST['slot_id']
        slot = get_object_or_404(Slot, id=slot_id)
        patient_id = request.POST['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        try:
            appointee = patient
            appoint_status = 'Failed'
          
            instance = Appointment(appointee = appointee, appoint_status=appoint_status,slot=slot)
            
            instance.save()
          
    
            return redirect('initiate-payment', appoint_id=instance.appoint_id)
          
        except Exception as e:
                messages.error(request, "An error occurred while creating your appointment. Please try again later.")
                return redirect('create-appointment-patient')
        
    else:
        messages.error(request, "An error occurred while creating your appointment. Please try again later.")
        return redirect('create-appointment-patient')












#********* Create a view to show all patient appointments (by Patients)
def view_appointments(request):
    # Filter appointments based on the logged-in user
    user = request.user
    user_appointments = Appointment.objects.filter(appointee__user=user)
   

    for appointment in user_appointments:
        if appointment.slot.date < date.today() and appointment.appoint_status != 'Completed':
            appointment.appoint_status = 'Completed'
            appointment.save()
        appointment.payment_display = "✅️" if appointment.payment else "⚠️"
    
    return render(request, 'appoint_app/view_appointments.html', {'user_appointments': user_appointments,})



#************* Create a view to show all patient payments (by Patients)
def view_payments_patient(request):
    # Filter payments based on the logged-in user
    user = request.user
    user_payments = Payment.objects.filter(user=user)
    for payment in user_payments:
        payment.verified_display = "✅" if payment.verified else "⚠️" 
    
    return render(request, 'appoint_app/view_payments.html', {'user_payments': user_payments,})



#*********** Create a view for appointments' management (by Patients)
def view_appointments_manage(request):
     # Filter appointments based on the logged-in user
    user = request.user
    all_user_appointments = Appointment.objects.filter(appointee__user=user)
 
        

    for appointment in all_user_appointments:
        if appointment.slot.date < date.today() and appointment.appoint_status != 'Completed':
            appointment.appoint_status = 'Completed'
            appointment.save()
  
        appointment.phone_number = appointment.appointee.phone_number 
        appointment.payment_display = "✅️" if appointment.payment else "⚠️"

    return render(request, 'appoint_app/view_appointments_manage.html', {'all_user_appointments': all_user_appointments,})



# Create a view for video calls (for Patients)     
def video_call_patient(request):
    pass
    return render(request, "appoint_app/video_call_patient.html")      
  


#### Create a view for updating a patient's profile
def update_profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile update success!')
            return render(request, 'appoint_app/update_profile.html', {'profile': profile, 'form': form})
        else:
            return render(request, 'appoint_app/update_profile.html', {'profile': profile, 'form': form})
    else:
        form = UpdateProfileForm(instance=profile)
    return render(request, 'appoint_app/update_profile.html', {'profile': profile, 'form': form})






       








#************ Create a view for displaying a specific appointment
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appoint_id=appointment_id)
 
    appointment.payment_display = "✅️" if appointment.payment else "⚠️"
    return render(request, 'appoint_app/view_appointment.html', {'appointment': appointment})












# Manage all Appointments (by Admins)
def all_appointments(request):   
    appointments_list = Appointment.objects.all()

    for appointment in appointments_list:
        if appointment.slot.date < date.today() and appointment.appoint_status != 'Completed':
            appointment.appoint_status = 'Completed'
            appointment.save()
        user = appointment.appointee
        appointment.phone_number = user.phone_number 
        appointment.payment_display = "✅️" if appointment.payment else "⚠️"

    return render(request, 'appoint_app/view_appointment_list.html', {'appointments_list': appointments_list})




  


      
# View all user Payments (by Admins)
def all_payments(request):   
    all_user_payments = Payment.objects.all()

    for payment in all_user_payments: 
        payment.verified_display = "✅️" if payment.verified else "⚠️"

    return render(request, 'appoint_app/view_payments.html', {'user_payments': all_user_payments})    
    





#****************
# Create a view for all Closed appointments (for Doctors)
def closed_appointments(request):
    closed_appointments = Appointment.objects.filter(appointed_doctor=request.user, appoint_status__in=['Failed', 'Completed', 'Canceled']).order_by('-appoint_time')
    
    for appointment in closed_appointments:
        appointee = appointment.appointee

    
    return render(request, "appoint_app/closed_appointments.html", {'closed_appointments': closed_appointments})

#*****************
def cancel_appointment(request, appointment_id):
    
    appointment = get_object_or_404(Appointment, appoint_id=appointment_id)

    if request.method == 'POST':
        try:
            # If the user confirms the cancellation
            appointment.appoint_status = "Canceled"
            #appointment.close_date = timezone.now()
            appointment.save()
            

            try:

                # Send an email to the patient
                subject = 'Your Appointment Has Been Cancelled'
                email_from = settings.EMAIL_HOST_USER
                message = (f"Hello, ! Your appointment {appointment.appoint_id} has been cancelled. Akankha Homeo™ ")
                send_mail(subject, message, email_from, [appointment.appointee.user.email])
            except Exception as e:
                messages.error(request, "Oops! An error occurred while sending the cancellation email. Check your internet connection.")
                appointment.appoint_status = "Scheduled"  # Rollback appointment status
                appointment.is_resolved = False
                appointment.close_date = None
                appointment.save()
                return redirect('cancel_patient_appointment', appointment_id=appointment_id)

            messages.success(request, 'Appointment has been cancelled successfully.')
            return redirect('appointments-list')  # Redirect to a page after cancellation
        except Exception as e:
            messages.error(request, 'An error occurred while cancelling the appointment. Please try again later.')
            return redirect('cancel_patient_appointment', appointment_id=appointment_id)

    return render(request, 'appoint_app/cancel_patient_appointment.html', {'appointment': appointment})

  



def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appoint_id=appointment_id)

    if request.method == 'POST':
        deleted_appointment_id = appointment.appoint_id
        try:
            # Send an email to the patient
       
            subject = f'Your Appointment {appointment.appoint_id} Has Been Deleted'
            email_from = settings.EMAIL_HOST_USER
            message = (f"Hello, {appointment.appointee}! Your appointment {appointment.appoint_id} has been deleted. "
                       "Akankha Homeo™ ")
            send_mail(subject, message, email_from, [appointment.appointee.user.email])

            appointment.delete()
        except Exception as e:
            messages.error(request, "Oops! An error occurred while sending the deletion email or deleting the appointment. Check your internet connection and try again.")
            return redirect('delete_patient_appointment', appointment_id=appointment_id)

        messages.success(request, f'Your appointment {deleted_appointment_id} has been deleted.')
        return redirect('appointments-list')  # Redirect to appointments management page after deletion

    return render(request, 'appoint_app/delete_patient_appointment.html', {'appointment': appointment})
  




def create_auto_slot(request):
    try:
        last_update = Misc.objects.last()
        next_date = last_update.to_date + timedelta(days=1)
    except:
        next_date = date.today()
        

    if request.method == 'POST':
        form = Create_auto_slot(request.POST)
        
        if form.is_valid():
            try:
                x = Schedule.objects.all()
                
                sc = form.save(commit=False)
             
                from_date = sc.from_date
                from_d = from_date
                to_date = sc.to_date
                count = 0
                while (from_date <= to_date):
                    for i in x:
                        if i.day == from_date.weekday():
                            slot=Slot(centre=i.centre, date=from_date, start_time=i.start_time, end_time=i.end_time,allowed=i.allowed)
                            slot.save()
                            count+=1
                    from_date += timedelta(days=1)
                misc = Misc(from_date=from_d, to_date=to_date)
                
                misc.save()
            
                messages.success(request, f"{count} new slot added successfully!")
                return redirect('admin:appoint_app_slot_changelist')
            except:
                messages.error = (request, 'Oops! Something went wrong, try again.')
                return render(request,'appoint_app/create_auto_slot.html',{'form': form, 'last_update':last_update, 'next_date':next_date})


    form = Create_auto_slot()
    return render(request,'appoint_app/create_auto_slot.html',{'form': form, 'last_update':last_update, 'next_date':next_date})