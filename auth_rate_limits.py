"""
Rate Limiting Configuration for Authentication Routes

This module applies rate limits to authentication endpoints to prevent:
- Brute force password attacks
- Account enumeration
- Spam signups
"""

def apply_auth_rate_limits(app, auth_bp):
    """
    Apply rate limits to authentication routes

    Args:
        app: Flask application instance
        auth_bp: Authentication blueprint
    """
    limiter = app.limiter

    # Apply rate limits to specific auth routes
    # These limits are applied after the blueprint is registered

    # Login - prevent brute force attacks
    limiter.limit("5 per minute", per_method=True)(
        app.view_functions.get('auth.login')
    )

    # Signup - prevent spam registrations
    limiter.limit("3 per hour", per_method=True)(
        app.view_functions.get('auth.signup')
    )

    # Password reset/verification resend - prevent abuse
    limiter.limit("3 per hour", per_method=True)(
        app.view_functions.get('auth.resend_verification')
    )

    # Admin endpoints - stricter limits
    if 'auth.admin_toggle_user_active' in app.view_functions:
        limiter.limit("10 per hour")(
            app.view_functions.get('auth.admin_toggle_user_active')
        )

    if 'auth.admin_delete_user' in app.view_functions:
        limiter.limit("5 per hour")(
            app.view_functions.get('auth.admin_delete_user')
        )

    print("✓ Rate limits applied to authentication routes")
