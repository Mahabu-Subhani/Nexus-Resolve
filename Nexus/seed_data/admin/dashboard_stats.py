class DashboardStats:
    """No payment provider coupling, reads from internal analytics DB only."""
    def get_daily_active_users(self, date):
        return AnalyticsDB.query_dau(date)

    def get_signup_funnel(self):
        return AnalyticsDB.query_funnel()
