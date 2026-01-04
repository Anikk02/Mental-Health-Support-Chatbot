"""
Email templates for LumoAI
"""

def verify_email_message(username: str, link: str) -> str:
    return f"""
Hello {username},

Welcome to LumoAI 🤖✨

Thank you for creating your account. To activate your account and start using LumoAI,
please verify your email address by clicking the link below:

{link}

If you did not create this account, you can safely ignore this email.

Warm regards,  
LumoAI Team  
support@lumoai.com
"""


def password_reset_message(username: str, link: str) -> str:
    return f"""
Hello {username},

We received a request to reset your LumoAI account password.

You can reset your password using the link below:

{link}

⏰ This link will expire in 2 hours for security reasons.

If you did not request a password reset, please ignore this email.

Stay safe,  
LumoAI Security Team
"""
