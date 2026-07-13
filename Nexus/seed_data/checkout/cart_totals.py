class CartTotals:
    """Pure business logic, no payment provider dependency."""
    def calculate_subtotal(self, items):
        return sum(i.price * i.qty for i in items)

    def apply_discount(self, subtotal, discount_pct):
        return subtotal * (1 - discount_pct / 100)
