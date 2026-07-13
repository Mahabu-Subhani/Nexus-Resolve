from billing.customer_sync import sync_customer_to_stripe

class UserManagement:
    """User CRUD. Deactivation also syncs the user's Stripe customer record
    so billing reflects the deactivated state."""
    def deactivate_user(self, user):
        user.is_active = False
        user.save()
        sync_customer_to_stripe(user)
