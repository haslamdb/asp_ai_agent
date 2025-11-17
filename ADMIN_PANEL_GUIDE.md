# Admin Panel Guide

## Overview

A comprehensive admin dashboard has been added to the ASP AI Agent for managing users, viewing activity, and monitoring system usage.

## Features

### 📊 Dashboard Statistics
- **Total Users**: Count of all registered users
- **Active Users**: Users with active accounts (not blocked)
- **New This Week**: Users who signed up in the last 7 days
- **Total Sessions**: Cumulative count of all training sessions

### 👥 User Management
- View all users with detailed information
- Search/filter users by name, email, or institution
- See user activity (sessions, module progress)
- View email verification status
- See admin/blocked status

### 🔧 Admin Actions
For each user, admins can:
- **View Details**: See full profile, recent sessions, and module progress
- **Block/Unblock**: Toggle user active status to prevent login
- **Delete**: Permanently remove user and all their data
- **Make Admin**: Promote user to admin privileges

### 🛡️ Security Features
- **Admin-only access**: Only users with `is_admin=True` can access
- **Protected accounts**: Cannot block/delete yourself or other admins
- **Confirmation prompts**: Double-confirmation for destructive actions

## Access

### For Admin Users
1. Login to your account
2. You'll see an **"Admin Panel"** link in the navigation
3. Click to access the admin dashboard
4. URL: `https://50.5.30.133:443/admin`

### For Non-Admin Users
- The admin panel link won't appear
- Direct access attempts will return 403 Forbidden

## Admin Routes

### Dashboard
```
GET /admin
```
The main admin dashboard with statistics and user table

### API Endpoints
```
GET  /api/admin/stats                     - System statistics
GET  /api/admin/users                     - List all users with activity
GET  /api/admin/users/{id}                - Get user details
POST /api/admin/users/{id}/toggle-active  - Block/unblock user
POST /api/admin/users/{id}/make-admin     - Promote to admin
DELETE /api/admin/users/{id}/delete       - Delete user
```

## Using the Admin Panel

### 1. Viewing Statistics
The top of the dashboard shows:
- Total users
- Active users (not blocked)
- New users this week
- Total training sessions

### 2. Managing Users

**Search Users:**
- Use the search box to filter by name, email, or institution
- Results update in real-time as you type

**View User Details:**
- Click "View" next to any user
- See their profile information
- Review recent sessions (last 10)
- Check module progress

**Block/Unblock User:**
- Click "Block" to prevent user from logging in
- Click "Unblock" to restore access
- Blocked users show red "Blocked" badge
- They can still receive verification emails

**Make User Admin:**
- Click "Make Admin" to promote user
- Admin users can access the admin panel
- Admin users cannot be blocked or deleted

**Delete User:**
- Click "Delete" to permanently remove user
- Requires double confirmation
- Deletes ALL user data:
  - User account
  - Sessions
  - Progress
  - Cannot be undone!

### 3. User Table Columns

| Column | Description |
|--------|-------------|
| User | Name, email, verification status (✓ or ✗) |
| Institution | Institution and specialty |
| Activity | Session count and module completion |
| Status | Active/Blocked badge, Admin badge |
| Last Login | Last successful login timestamp |
| Actions | View, Block/Unblock, Make Admin, Delete |

### 4. User Details Modal

Click "View" to see:
- **Profile Information**: Email, name, institution, fellowship year, specialty
- **Recent Sessions**: Last 10 sessions with timestamps and models used
- **Module Progress**: All modules with completion status and scores

## Installation & Setup

The admin panel is now installed. To activate:

1. **Restart the server:**
   ```bash
   sudo systemctl restart asp-ai-agent
   ```

2. **Wait 30 seconds** for the server to fully start

3. **Login** as an admin user:
   - Default admin: `admin@asp-ai-agent.com`
   - Or any user with `is_admin=True`

4. **Click "Admin Panel"** in the navigation

## Creating Additional Admins

### Method 1: Via Admin Panel
1. Login as an existing admin
2. Go to Admin Panel
3. Find the user you want to promote
4. Click "Make Admin"

### Method 2: Via Database
```python
python3 << EOF
from unified_server import app
from auth_models import db, User

with app.app_context():
    user = User.query.filter_by(email='user@example.com').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"{user.email} is now an admin")
    else:
        print("User not found")
EOF
```

### Method 3: Via SQL
```bash
sqlite3 instance/asp_ai_agent.db "UPDATE users SET is_admin=1 WHERE email='user@example.com'"
```

## Security Considerations

### Access Control
- Admin routes use `@admin_required` decorator
- Checks both authentication and admin status
- Returns 403 Forbidden for non-admins

### Protected Operations
- Cannot block yourself
- Cannot delete yourself
- Cannot block other admins
- Cannot delete other admins
- All destructive actions require confirmation

### Audit Trail
- All user sessions are logged in `UserSession` table
- Track when users log in (`last_login`)
- Monitor module progress

## Troubleshooting

### "403 Forbidden" when accessing /admin
**Cause**: Your account is not an admin

**Solution**:
```python
python3 << EOF
from unified_server import app
from auth_models import db, User

with app.app_context():
    user = User.query.filter_by(email='YOUR_EMAIL').first()
    user.is_admin = True
    db.session.commit()
    print("You are now an admin")
EOF
```

### Admin Panel link not showing
**Cause**: You're not logged in as an admin

**Solution**:
1. Logout
2. Make your account admin (see above)
3. Login again
4. Admin Panel link will appear

### Cannot delete user
**Cause**: Trying to delete admin or yourself

**Solution**: Admin accounts are protected. If you really need to delete an admin, first demote them:
```bash
sqlite3 instance/asp_ai_agent.db "UPDATE users SET is_admin=0 WHERE id=USER_ID"
```

## Best Practices

1. **Limit admin access**: Only promote trusted users to admin
2. **Regular audits**: Review user activity periodically
3. **Communicate before blocking**: Warn users before blocking their accounts
4. **Backup before deleting**: User deletion is permanent
5. **Monitor new signups**: Check for spam/fake accounts
6. **Review sessions**: Look for unusual activity patterns

## Future Enhancements

Potential additions:
- Export user data to CSV
- Bulk user operations
- Activity logs/audit trail
- Email users directly from panel
- Session analytics and graphs
- Module completion reports
- User groups/roles
- Custom permissions

## Support

For issues or questions:
- Check the logs: `sudo journalctl -u asp-ai-agent -n 100`
- Verify database: `sqlite3 instance/asp_ai_agent.db "SELECT * FROM users"`
- Restart service: `sudo systemctl restart asp-ai-agent`
