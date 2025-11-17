# Email Verification Setup Guide

## Overview

Email verification has been added to the ASP AI Agent authentication system. New users must verify their email address before they can log in.

## Features

✅ **Email verification on signup** - Users receive a verification link via email
✅ **24-hour token expiry** - Verification links expire after 24 hours
✅ **Resend verification** - Users can request a new verification email
✅ **Login protection** - Unverified users cannot log in
✅ **Graceful fallback** - If email isn't configured, links print to console

## How It Works

### 1. User Signup Flow

```
User signs up → Account created → Verification email sent → User clicks link → Email verified → User can login
```

### 2. If Email Not Configured

When SMTP settings are not configured in `.env`, the system will:
- Still create the user account
- Print the verification link to the server console
- Show a message to the user explaining the situation
- Allow manual verification via the console link

## Email Configuration

### Option 1: Gmail (Recommended for Testing)

1. **Create a Gmail App Password**:
   - Go to https://myaccount.google.com/security
   - Enable 2-Factor Authentication (required)
   - Go to https://myaccount.google.com/apppasswords
   - Create an app password for "Mail"
   - Copy the 16-character password

2. **Update `.env` file**:
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   FROM_EMAIL=your-email@gmail.com
   FROM_NAME=ASP AI Agent
   BASE_URL=https://50.5.30.133:443
   ```

### Option 2: Other Email Providers

#### SendGrid
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

#### AWS SES
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-access-key
SMTP_PASSWORD=your-ses-secret-key
FROM_EMAIL=noreply@yourdomain.com
```

#### Mailgun
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-smtp-password
FROM_EMAIL=noreply@yourdomain.com
```

### Option 3: No Email (Console Mode)

Leave SMTP settings blank in `.env`:
```bash
SMTP_USERNAME=
SMTP_PASSWORD=
```

The system will print verification links to the console.

## Configuration Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BASE_URL` | Yes | Base URL for verification links | `https://50.5.30.133:443` |
| `SMTP_SERVER` | No* | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | No* | SMTP server port | `587` |
| `SMTP_USERNAME` | No* | SMTP username/email | `your-email@gmail.com` |
| `SMTP_PASSWORD` | No* | SMTP password/app password | `abcdefghijklmnop` |
| `FROM_EMAIL` | No | Sender email address | `noreply@yourdomain.com` |
| `FROM_NAME` | No | Sender display name | `ASP AI Agent` |

*If not configured, links will print to console

## Deployment & Testing

### 1. Update Environment Variables

Edit `/home/david/projects/asp_ai_agent/.env` with your email settings.

### 2. Restart the Application

```bash
sudo systemctl restart asp-ai-agent
```

### 3. Test the Flow

#### Test Signup:
```bash
# Open in browser
https://50.5.30.133:443/signup

# Or test via curl
curl -X POST https://50.5.30.133:443/signup \
  -k \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "full_name": "Test User"
  }'
```

#### Check Console for Verification Link (if email not configured):
```bash
sudo journalctl -u asp-ai-agent -f
```

Look for output like:
```
================================================================================
EMAIL VERIFICATION LINK (email not configured):
https://50.5.30.133:443/verify-email?token=abc123...
================================================================================
```

#### Test Verification:
```bash
# Click the link or curl it
curl -k "https://50.5.30.133:443/verify-email?token=abc123..."
```

#### Test Login (should work after verification):
```bash
https://50.5.30.133:443/login
```

## API Endpoints

### POST /signup
Creates new user and sends verification email
```json
{
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "full_name": "John Doe",
  "institution": "Hospital Name",
  "fellowship_year": 2,
  "specialty": "Infectious Disease"
}
```

### GET /verify-email?token={token}
Verifies user's email address

### POST /resend-verification
Resends verification email
```json
{
  "email": "user@example.com"
}
```

### POST /login
Login (requires verified email)
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

## Database Schema Changes

New fields added to `User` model:

```python
verification_token = db.Column(db.String(100), unique=True)
verification_token_expires = db.Column(db.DateTime)
```

## Troubleshooting

### Issue: Emails not sending

**Check:**
1. SMTP credentials are correct in `.env`
2. For Gmail: App password is used (not regular password)
3. For Gmail: 2FA is enabled on the account
4. Server can reach SMTP server on port 587
5. Check application logs: `sudo journalctl -u asp-ai-agent -n 50`

**Test SMTP connection:**
```python
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print('✓ SMTP connection successful!')
server.quit()
"
```

### Issue: Verification link expired

Users can click "Resend Verification Email" button on the login page.

### Issue: User can't receive emails

1. Check spam/junk folder
2. Verify email address is correct
3. Use console mode for testing
4. Check SPF/DKIM records if using custom domain

### Issue: Existing users can't log in

Existing users (created before email verification) will have `email_verified=False`.

**Options:**
1. Have them verify via new verification email
2. Manually verify them in database:
   ```bash
   sqlite3 asp_sessions.db "UPDATE users SET email_verified=1"
   ```

## Security Considerations

✅ **Token security**: Uses cryptographically secure random tokens
✅ **Token expiry**: 24-hour expiration prevents stale links
✅ **One-time use**: Tokens are cleared after use
✅ **No user enumeration**: "Email sent" message shown even if user doesn't exist
✅ **HTTPS required**: Verification links use HTTPS

## Production Recommendations

1. **Use a dedicated email service** (SendGrid, AWS SES, Mailgun)
   - Better deliverability
   - Better analytics
   - Higher sending limits

2. **Set up SPF and DKIM** for your domain
   - Improves email deliverability
   - Reduces spam classification

3. **Monitor email sending**
   - Track delivery rates
   - Set up alerts for failures

4. **Consider rate limiting**
   - Limit verification email requests per IP
   - Prevent abuse

5. **Use your own domain**
   - More professional
   - Better trust signals
   - Replace `BASE_URL` with `https://asp-ai-agent.com:8443`

## Testing Checklist

- [ ] User can sign up
- [ ] Verification email is sent/printed to console
- [ ] Verification link works
- [ ] Verified user can log in
- [ ] Unverified user cannot log in
- [ ] "Resend verification" works
- [ ] Expired tokens show correct error
- [ ] Invalid tokens show correct error

## Support

If you encounter issues:

1. Check the application logs
2. Verify `.env` configuration
3. Test SMTP connection
4. Use console mode for debugging
