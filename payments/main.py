
import razorpay
from django.conf import settings


client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET
    )
)

class RazorpayClient:

    def create_order(self, amount, currency):
        data = {
            "amount": amount * 100,
            "currency": currency,
        }
        self.order = client.order.create(data=data)
        return self.order
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        try:
            return client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
            })
        except:
            return False