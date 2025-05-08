from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import HttpRequest, HttpResponse

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import Payment
from appoint_app.models import Appointment
from django.db import models
from django.utils import timezone

#set Payment ammount
amount = 50000

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def initiate_payment(request: HttpRequest, appoint_id) -> HttpResponse:
    currency = 'INR'
 

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    
    callback_url = "http://127.0.0.1:8000/payments/paymenthandler/"

    appointment = get_object_or_404(Appointment, appoint_id=appoint_id)

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    context['patient'] = appointment.appointee
    context['date'] = appointment.slot.date
    context['centre'] = appointment.slot.centre
    context['amount'] = amount/100

    appointment = get_object_or_404(Appointment, appoint_id=appoint_id)

    payment_instance = Payment(user = request.user,amount=amount/100, appointment = appointment,order_id= razorpay_order_id )
    payment_instance.save()

    return render(request, 'payments/initiate_payment_copy.html', context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    

    # only accept POST request.
    if request.method == "POST":
        

        
        try:
         
          
            # get the required parameters from post request.
            
            payment_id = request.POST.get('razorpay_payment_id', '')
           
            
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            
            signature = request.POST.get('razorpay_signature', '')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)

            
            
            
            
            if result is not None:
                

                try:
                     # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    payment = get_object_or_404(Payment,order_id = razorpay_order_id)
                    payment.verified = True

                
                    payment.save()
                    
                    appointment = payment.appointment

                  
                    appointment.appoint_status = 'Scheduled'
                    appointment.approve_date = timezone.now()
                    appointment.payment = True
                    
                    appointment.save()
                    # render success page on successful caputre of payment
                    return render(request, 'payments/payment_success.html')
            
                except:
                    

                    # if there is an error while capturing payment.
                 
                    return render(request, 'payments/payment_failed.html')
            else:

                # if signature verification fails.
                return render(request, 'payments/payment_failed.html')
        except:
      
       
            # if we don't find the required parameters in POST data
            post_data = request.POST.get('error[description]')
            return render(request, 'payments/payment_failed.html', {'context':post_data})
    else:
       # if other than POST request is made.
   
        return HttpResponseBadRequest()
    

def cancel_payment(request):
    return render(request, 'payments/payment_failed.html')