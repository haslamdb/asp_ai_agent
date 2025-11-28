"""
Email Utilities for ASP AI Agent
Handles sending verification emails, password resets, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user_email: str, user_name: str, verification_token: str, base_url: str) -> bool:
    """
    Send email verification link to user

    Args:
        user_email: User's email address
        user_name: User's full name
        verification_token: Unique verification token
        base_url: Base URL of the application (e.g., https://asp-ai-agent.com:8443)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_username)
    from_name = os.getenv('FROM_NAME', 'ASP AI Agent')

    # Check if email is configured
    if not smtp_username or not smtp_password:
        logger.warning("Email not configured - SMTP_USERNAME or SMTP_PASSWORD missing")
        print(f"\n{'='*80}")
        print("EMAIL VERIFICATION LINK (email not configured):")
        print(f"{base_url}/verify-email?token={verification_token}")
        print(f"{'='*80}\n")
        return False

    # Build verification URL
    verification_url = f"{base_url}/verify-email?token={verification_token}"

    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Verify your ASP AI Agent account'
    msg['From'] = f'{from_name} <{from_email}>'
    msg['To'] = user_email

    # Plain text version
    text_body = f"""
Hello {user_name},

Thank you for signing up for ASP AI Agent!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create this account, you can safely ignore this email.

Best regards,
ASP AI Agent Team
"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 28px;">ASP AI Agent</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Antimicrobial Stewardship Training Platform</p>
    </div>

    <div style="background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
        <h2 style="color: #1f2937; margin-top: 0;">Hello {user_name},</h2>

        <p>Thank you for signing up for ASP AI Agent! We're excited to have you join our antimicrobial stewardship training platform.</p>

        <p>Please verify your email address by clicking the button below:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white;
                      padding: 14px 30px;
                      text-decoration: none;
                      border-radius: 8px;
                      display: inline-block;
                      font-weight: bold;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                Verify Email Address
            </a>
        </div>

        <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link into your browser:</p>
        <p style="background: white; padding: 12px; border: 1px solid #e5e7eb; border-radius: 6px; word-break: break-all; font-size: 13px; color: #4b5563;">
            {verification_url}
        </p>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <p style="color: #6b7280; font-size: 13px; margin: 5px 0;">
                <strong>Note:</strong> This verification link will expire in 24 hours.
            </p>
            <p style="color: #6b7280; font-size: 13px; margin: 5px 0;">
                If you did not create this account, you can safely ignore this email.
            </p>
        </div>

        <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
            <p style="color: #1e40af; font-size: 13px; margin: 0; line-height: 1.6;">
                <strong>Privacy Notice:</strong> Chat histories are not stored, nor are your responses to questions in the training modules.
                However, your progress through the ASP curriculum and scores achieved on each module will be
                saved in the ASP AI Agent database to track your learning journey. You may retake any module
                at any time, which will update your previous scores for that module.
            </p>
        </div>

        <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>ASP AI Agent Team</strong>
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 12px;">
        <p>© 2025 ASP AI Agent. All rights reserved.</p>
    </div>
</body>
</html>
"""

    # Attach both parts
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        logger.info(f"Verification email sent to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
        print(f"\n{'='*80}")
        print("FAILED TO SEND EMAIL - Verification link (for testing):")
        print(f"{verification_url}")
        print(f"Error: {str(e)}")
        print(f"{'='*80}\n")
        return False


def send_password_reset_email(user_email: str, user_name: str, reset_token: str, base_url: str) -> bool:
    """
    Send password reset link to user

    Args:
        user_email: User's email address
        user_name: User's full name
        reset_token: Unique reset token
        base_url: Base URL of the application

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # This can be implemented similarly to verification email
    # Left as placeholder for future implementation
    pass
