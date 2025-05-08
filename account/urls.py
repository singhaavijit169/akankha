from django.urls import path, include
from account import views
from appoint_app.views import dashboard, home, terms
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path("video-call-patient/", views.video_call_patient, name='video-call-patient'),
    
    # ---------- Register \ LogIN \Logout \ delet \UPDAYTEuser-------------#

    path("login/", views.login_user, name='login'),
    path("logout/", views.logout_user, name='logout'),
    path("log/", views.admin_otp_verification, name='admin_otp_verification'),
    path("reg/", views.reg_otp_verification, name='reg_otp_verification'),


    path('register-patient/', views.register_patient, name='register-patient'),
    path("update-profile/<str:username>/", views.update_profile, name='update-profile'),


    path('delete_account_confirmation/', views.delete_account_confirmation, name='delete_account_confirmation'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
   

# ------------  Land Portal --------------
    path('patients-portal/',dashboard , name='patients_portal'),
    path('admins-portal/', dashboard, name='admins_portal'),


# -----------View/manage Appointments --------------------
    path("view-appointments/", views.view_appointments, name='view-appointments'),
    path("view-appointments-manage/", views.view_appointments_manage, name='view-appointments-manage'),
    path("view-appointment/<str:appointment_id>/", views.view_appointment, name='view-appointment'),
    path("appointments-list/", views.all_appointments, name='appointments-list'),
    
    

    

    #path("approved-appointments/", views.approved_appointments, name='approved-appointments'),
    #path("view-all-appointments/", views.view_all_appointments, name='view-all-appointments'),

    #path("view-appointment-patient/<str:appointment_id>/", views.view_appointment_patient, name='view-appointment-patient'),

    #path("close-appointment/<str:appointment_id>/", views.close_appointment, name='close-appointment'),
    #path("closed-appointments/", views.closed_appointments, name='closed-appointments'),
    path("cancel-appointment/<str:appointment_id>/", views.cancel_appointment, name='cancel-appointment'),
    path("delete-appointment/<str:appointment_id>/", views.delete_appointment, name='delete-appointment'),




# --------------------- Create Appointmet /SLOT ----------------------

    path("create-appointment-patient/", views.create_appointment_patient, name='create-appointment-patient'),


    path("book_slot_patient/", views.book_slot_patient, name='book-slot-patient'),
    path("create_auto_slot/",views.create_auto_slot,name='create-auto-slot'),


# ----------- PDFs ----------------------


    path('account/export_appointment_pdf/<str:appointment_id>/', views.export_appointment_pdf, name='export_appointment_pdf'),
    path('export/appointments_payments/pdf/', views.export_appointments_payments_pdf, name='export_appointments_payments_pdf'),
    path('export_user_payments_pdf/', views.export_user_payments_pdf, name='export_user_payments_pdf'),
    path('export_admin_all_payments_pdf/', views.export_admin_all_payments_pdf, name='export_admin_all_payments_pdf'),
     

   
    

   
   



# ---------------------- Payments --------------
  

    path("all-payments/", views.view_payments_patient, name='all-payments'),


    path("manage-user-payments/", views.all_payments, name='manage-user-payments'),

    
# ****************************************
    path("", include('django.contrib.auth.urls')),
]