# Quick Test: Email Verification

## Test Without Email Configuration (Console Mode)

Since you haven't configured SMTP yet, the system will print verification links to the console.

### 1. Watch the Application Logs

Open a terminal and run:
```bash
sudo journalctl -u asp-ai-agent -f
```

### 2. Create a Test User

Open another terminal or browser and sign up:

**Via Browser:**
```
https://50.5.30.133:443/signup
```

**Via curl:**
```bash
curl -k -X POST https://50.5.30.133:443/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "full_name": "Test User"
  }'
```

### 3. Find the Verification Link

In the logs (first terminal), you'll see:
```
================================================================================
EMAIL VERIFICATION LINK (email not configured):
https://50.5.30.133:443/verify-email?token=abc123...
================================================================================
```

### 4. Click the Verification Link

Copy the link and open it in your browser, or:
```bash
curl -k "https://50.5.30.133:443/verify-email?token=PASTE_TOKEN_HERE"
```

### 5. Login

After verification, you can login:
```
https://50.5.30.133:443/login
```
Use:
- Email: test@example.com
- Password: testpass123

### 6. Test Unverified User Login

Try to create another user but DON'T verify them. Then try to login - you should see:
```
"Please verify your email address before logging in"
```
With a "Resend Verification Email" button.

## Test With Email Configuration

### Setup Gmail (for testing)

1. Get a Gmail App Password:
   - https://myaccount.google.com/apppasswords

2. Edit `.env`:
   ```bash
   nano /home/david/projects/asp_ai_agent/.env
   ```

3. Add:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   FROM_EMAIL=your-email@gmail.com
   ```

4. Restart:
   ```bash
   sudo systemctl restart asp-ai-agent
   ```

5. Sign up with a real email address

6. Check your inbox for the verification email

7. Click the link in the email

8. Login successfully

## Expected Behavior

✅ **Signup Page** → User fills form → Redirected to "Check Your Email" page
✅ **Email Sent** → User receives professional-looking verification email
✅ **Click Link** → User sees "Email Verified!" success page
✅ **Login** → User can now login to dashboard
✅ **Unverified Login Attempt** → Shows "Email Verification Required" page
✅ **Resend Verification** → User can request new link if expired/lost

## Screenshots of New Pages

### 1. After Signup
- "Check Your Email" page with instructions
- Shows email address where link was sent
- "Resend Verification Email" button

### 2. After Clicking Link
- "Email Verified!" success page
- "Sign In Now" button

### 3. Unverified Login Attempt
- "Email Verification Required" page
- Shows why they can't login
- "Resend Verification Email" button

### 4. Link Expired
- "Link Expired" page
- Explains 24-hour expiration
- "Send New Verification Email" button

## Troubleshooting

### "No such table: users"
The database will be created on first run. Just restart:
```bash
sudo systemctl restart asp-ai-agent
```

### Can't see verification link in logs
Make sure you're watching the right service:
```bash
sudo journalctl -u asp-ai-agent -f --no-pager
```

### Gmail rejects login
- Make sure you're using an App Password, not your regular password
- Make sure 2FA is enabled on your Google account
- Check: https://myaccount.google.com/apppasswords

### Email goes to spam
This is normal for testing. In production:
- Use a dedicated email service (SendGrid, AWS SES)
- Set up SPF/DKIM records
- Use your own domain

## Next Steps

1. **Test in Console Mode** (no email config) - Easiest for development
2. **Set up Gmail** - For realistic testing with real emails
3. **Configure Production Email** - SendGrid/AWS SES for production use
4. **Optional: Whitelist Existing Users** - If you have users before this update

## Whitelist Existing Users (Optional)

If you had users before adding email verification, you can manually verify them:

```python
python3 << EOF
from auth_models import db, User
from unified_server import app

with app.app_context():
    # Verify all existing users
    users = User.query.filter_by(email_verified=False).all()
    for user in users:
        user.email_verified = True
        print(f"Verified: {user.email}")
    db.session.commit()
    print(f"\nTotal users verified: {len(users)}")
EOF
```
