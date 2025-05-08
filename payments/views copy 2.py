from django.shortcuts import get_object_or_404, redirect, render
import razorpay
from appoint_app.models import Appointment
from django.http import HttpRequest, HttpResponse



def initiate_payment(request: HttpRequest, appoint_id) -> HttpResponse:
    razorpay_api_key = 'rzp_test_ee7OWqArzFFlQC'
    razorpay_secret_key = '08y4aj4jPvlgmOzPig1blZ5S'

    client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))
    appointment = get_object_or_404(Appointment, appoint_id=appoint_id)


    # Create an order
    response = client.order.create({
        'amount': 100,  # Amount in paise (change as per your requirement)
        'currency': 'INR',
        'payment_capture': 1  # Auto capture payment
    })

    order_id = response['id']
    context = {
        'order_id': order_id,
        'razorpay_api_key': razorpay_api_key, # Use this key in the frontend to create the payment form
        'appointment': appointment
    }

    return render(request, 'payments/payment.html', context)