import stripe
from billing.customer_sync import sync_customer_to_stripe

class SubscriptionManager:
    def create_subscription(self, user, price_id):
        customer_id = sync_customer_to_stripe(user)
        return stripe.Subscription.create(customer=customer_id, items=[{"price": price_id}])

    def cancel_subscription(self, subscription_id):
        return stripe.Subscription.delete(subscription_id)

    def update_payment_method(self, customer_id, payment_method_id):
        stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": payment_method_id})

    def list_invoices(self, customer_id):
        return stripe.Invoice.list(customer=customer_id)
