from django.urls import path
from .import views

urlpatterns = [
   
    path('initiate-payment/<str:appoint_id>/', views.initiate_payment, name="initiate-payment"),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('cancel-payment/', views.cancel_payment, name='cancel-payment'),

    

]