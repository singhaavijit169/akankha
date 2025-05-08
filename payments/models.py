from django.db import models
from django.utils import timezone


# Create a Payment model 
class Payment(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, blank=False, related_name='user')
    amount = models.PositiveBigIntegerField()
    appointment = models.ForeignKey('appoint_app.Appointment', on_delete=models.CASCADE, blank=True, null=True, related_name='payments')
    order_id = models.CharField('Order ID',max_length=20, blank=True, null=True)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date_created',]
                
    def amount_value(self) -> int:
        return self.amount * 100
        