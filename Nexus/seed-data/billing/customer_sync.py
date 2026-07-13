import stripe

def sync_customer_to_stripe(user):
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.full_name)
        user.stripe_customer_id = customer.id
        user.save()
    return user.stripe_customer_id
