import stripe
from stripe.error import CardError

stripe.api_key = settings.STRIPE_SECRET_KEY

class ChargeService:
    def create_charge(self, amount, customer_id):
        try:
            return stripe.Charge.create(amount=amount, currency="usd", customer=customer_id)
        except CardError as e:
            raise PaymentFailed(str(e))

    def refund_charge(self, charge_id, amount=None):
        return stripe.Refund.create(charge=charge_id, amount=amount)

    def get_charge_status(self, charge_id):
        charge = stripe.Charge.retrieve(charge_id)
        return charge.status
