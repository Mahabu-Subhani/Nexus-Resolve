import stripe
from django.conf import settings
from billing.charge_service import ChargeService
from billing.subscription_manager import SubscriptionManager

def handle_stripe_webhook(payload, sig_header):
    event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    if event["type"] == "charge.succeeded":
        ChargeService().get_charge_status(event["data"]["object"]["id"])
    elif event["type"] == "invoice.payment_failed":
        SubscriptionManager().list_invoices(event["data"]["object"]["customer"])
    return event
