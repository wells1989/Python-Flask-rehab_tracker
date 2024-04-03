"""
logged_in_user = session.get('logged_in_user')
        if not logged_in_user:
            return "Unauthorized", 401
"""

def check_log_in(session):
    logged_in_user = session.get('logged_in_user')
    return False if not logged_in_user else True
