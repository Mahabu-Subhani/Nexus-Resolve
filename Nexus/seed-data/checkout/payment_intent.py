import stripe
from billing.customer_sync import sync_customer_to_stripe

class PaymentIntentHandler:
    def create_intent(self, amount, currency, user):
        customer_id = sync_customer_to_stripe(user)
        return stripe.PaymentIntent.create(
            amount=amount, currency=currency, customer=customer_id,
            automatic_payment_methods={"enabled": True},
        )

    def confirm_intent(self, intent_id, payment_method_id):
        return stripe.PaymentIntent.confirm(intent_id, payment_method=payment_method_id)
