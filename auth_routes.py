"""
Authentication Routes
Handles user login, signup, logout, and session management
"""

from flask import Blueprint, request, jsonify, render_template_string, redirect, url_for, session as flask_session, abort
from flask_login import login_user, logout_user, login_required, current_user
from auth_models import db, User, UserSession, UserProgress
from email_utils import send_verification_email
from admin_dashboard_template import ADMIN_DASHBOARD_TEMPLATE
from datetime import datetime
from functools import wraps
import re
import os

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'GET':
        # Return signup page HTML
        return render_template_string(SIGNUP_TEMPLATE)

    # Handle POST request
    data = request.json if request.is_json else request.form

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    full_name = data.get('full_name', '').strip()
    institution = data.get('institution', '').strip()
    fellowship_year = data.get('fellowship_year')
    specialty = data.get('specialty', '').strip()

    # Validation
    errors = []

    if not email or not is_valid_email(email):
        errors.append('Valid email is required')

    if not password or len(password) < 8:
        errors.append('Password must be at least 8 characters')

    if password != confirm_password:
        errors.append('Passwords do not match')

    if not full_name:
        errors.append('Full name is required')

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        errors.append('Email already registered')

    if errors:
        if request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400
        return render_template_string(SIGNUP_TEMPLATE, errors=errors, data=data)

    # Create new user
    try:
        user = User(
            email=email,
            full_name=full_name,
            institution=institution,
            fellowship_year=int(fellowship_year) if fellowship_year else None,
            specialty=specialty
        )
        user.set_password(password)

        # Generate verification token
        verification_token = user.generate_verification_token()

        db.session.add(user)
        db.session.commit()

        # Get base URL for verification link
        base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))

        # Send verification email
        email_sent = send_verification_email(
            user_email=email,
            user_name=full_name,
            verification_token=verification_token,
            base_url=base_url
        )

        # Show success message with instructions to verify email
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Account created! Please check your email to verify your account.',
                'email_sent': email_sent,
                'redirect': '/verification-pending'
            })

        return render_template_string(VERIFICATION_PENDING_TEMPLATE, email=email, email_sent=email_sent)

    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'errors': [str(e)]}), 500
        return render_template_string(SIGNUP_TEMPLATE, errors=[str(e)], data=data)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)

    data = request.json if request.is_json else request.form
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)

    if not email or not password:
        error = 'Email and password are required'
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 400
        return render_template_string(LOGIN_TEMPLATE, error=error, email=email)

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        error = 'Invalid email or password'
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 401
        return render_template_string(LOGIN_TEMPLATE, error=error, email=email)

    if not user.is_active:
        error = 'Account has been deactivated'
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 403
        return render_template_string(LOGIN_TEMPLATE, error=error, email=email)

    # Check if email is verified
    if not user.email_verified:
        error = 'Please verify your email address before logging in. Check your inbox for the verification link.'
        if request.is_json:
            return jsonify({
                'success': False,
                'error': error,
                'email_verified': False,
                'user_id': user.id
            }), 403
        return render_template_string(
            VERIFICATION_REQUIRED_TEMPLATE,
            email=email,
            user_id=user.id
        )

    # Login successful
    login_user(user, remember=remember)
    user.update_last_login()

    if request.is_json:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'redirect': '/dashboard'
        })

    next_page = request.args.get('next')
    return redirect(next_page if next_page else '/dashboard')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return render_template_string(LOGOUT_TEMPLATE)


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's recent sessions
    recent_sessions = UserSession.query.filter_by(
        user_id=current_user.id
    ).order_by(UserSession.started_at.desc()).limit(10).all()

    # Get user progress
    progress = UserProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template_string(
        DASHBOARD_TEMPLATE,
        user=current_user,
        recent_sessions=recent_sessions,
        progress=progress
    )


@auth_bp.route('/api/user/profile')
@login_required
def get_profile():
    """Get current user profile"""
    return jsonify(current_user.to_dict())


@auth_bp.route('/api/user/sessions')
@login_required
def get_user_sessions():
    """Get user's session history"""
    limit = request.args.get('limit', 20, type=int)
    sessions = UserSession.query.filter_by(
        user_id=current_user.id
    ).order_by(UserSession.started_at.desc()).limit(limit).all()

    return jsonify({
        'sessions': [s.to_dict() for s in sessions],
        'count': len(sessions)
    })


@auth_bp.route('/api/user/progress')
@login_required
def get_user_progress():
    """Get user's progress tracking"""
    progress = UserProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    return jsonify({
        'progress': [p.to_dict() for p in progress],
        'count': len(progress)
    })


@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    """Verify user's email address using token"""
    token = request.args.get('token')

    if not token:
        return render_template_string(
            VERIFICATION_ERROR_TEMPLATE,
            error='No verification token provided'
        ), 400

    # Find user with this token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return render_template_string(
            VERIFICATION_ERROR_TEMPLATE,
            error='Invalid verification token'
        ), 400

    # Check if token is valid and not expired
    if not user.is_verification_token_valid(token):
        return render_template_string(
            VERIFICATION_EXPIRED_TEMPLATE,
            email=user.email,
            user_id=user.id
        ), 400

    # Verify the email
    user.verify_email()

    return render_template_string(VERIFICATION_SUCCESS_TEMPLATE)


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    data = request.json if request.is_json else request.form
    email = data.get('email', '').strip().lower()

    if not email:
        user_id = data.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                email = user.email

    if not email:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        return 'Email is required', 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # Don't reveal if user exists for security
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'If an account exists with this email, a verification link has been sent.'
            })
        return render_template_string(
            VERIFICATION_PENDING_TEMPLATE,
            email=email,
            email_sent=True
        )

    if user.email_verified:
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Email is already verified',
                'redirect': '/login'
            }), 400
        return redirect('/login')

    # Generate new verification token
    verification_token = user.generate_verification_token()
    db.session.commit()

    # Get base URL
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))

    # Send verification email
    email_sent = send_verification_email(
        user_email=email,
        user_name=user.full_name,
        verification_token=verification_token,
        base_url=base_url
    )

    if request.is_json:
        return jsonify({
            'success': True,
            'message': 'Verification email sent! Please check your inbox.',
            'email_sent': email_sent
        })

    return render_template_string(
        VERIFICATION_PENDING_TEMPLATE,
        email=email,
        email_sent=email_sent,
        resent=True
    )


# HTML Templates (will be moved to separate files later)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-900">ASP AI Agent</h1>
                <p class="text-gray-600 mt-2">Antimicrobial Stewardship Training</p>
            </div>

            {% if error %}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {{ error }}
            </div>
            {% endif %}

            <form method="POST" action="/login" class="space-y-6">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" name="email" value="{{ email or '' }}" required
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <input type="password" name="password" required
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                </div>

                <div class="flex items-center">
                    <input type="checkbox" name="remember" id="remember"
                           class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                    <label for="remember" class="ml-2 block text-sm text-gray-700">Remember me</label>
                </div>

                <button type="submit"
                        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-200">
                    Sign In
                </button>
            </form>

            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600">
                    Don't have an account?
                    <a href="/signup" class="font-medium text-indigo-600 hover:text-indigo-500">Sign up</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
'''

SIGNUP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-900">Create Account</h1>
                <p class="text-gray-600 mt-2">Join ASP AI Agent Training Platform</p>
            </div>

            {% if errors %}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                <ul class="list-disc list-inside">
                {% for error in errors %}
                    <li>{{ error }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}

            <form method="POST" action="/signup" class="space-y-6">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                        <input type="text" name="full_name" value="{{ data.full_name if data else '' }}" required
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                        <input type="email" name="email" value="{{ data.email if data else '' }}" required
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Password *</label>
                        <input type="password" name="password" required
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                        <p class="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Confirm Password *</label>
                        <input type="password" name="confirm_password" required
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Institution</label>
                        <input type="text" name="institution" value="{{ data.institution if data else '' }}"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Fellowship Year</label>
                        <select name="fellowship_year"
                                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select year</option>
                            <option value="1">Year 1</option>
                            <option value="2">Year 2</option>
                            <option value="3">Year 3</option>
                        </select>
                    </div>

                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Specialty</label>
                        <input type="text" name="specialty" value="{{ data.specialty if data else '' }}"
                               placeholder="e.g., Infectious Disease, Pediatric ID"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>

                <button type="submit"
                        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition duration-200">
                    Create Account
                </button>
            </form>

            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600">
                    Already have an account?
                    <a href="/login" class="font-medium text-indigo-600 hover:text-indigo-500">Sign in</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
'''

LOGOUT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logged Out - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">✓</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">Successfully Logged Out</h1>
            <p class="text-gray-600 mb-6">You have been logged out of your account.</p>
            <a href="/login"
               class="inline-block bg-indigo-600 text-white py-2 px-6 rounded-lg hover:bg-indigo-700 transition duration-200">
                Sign In Again
            </a>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 min-h-screen">
    <nav class="bg-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">ASP AI Agent</h1>
                    <p class="text-sm text-gray-600">Welcome, {{ user.full_name }}!</p>
                </div>
                <div class="space-x-4">
                    <a href="/agent_models.html" class="text-indigo-600 hover:text-indigo-800">Training Modules</a>
                    <a href="/asp_ai_agent.html" class="text-indigo-600 hover:text-indigo-800">Chat</a>
                    {% if user.is_admin %}
                    <a href="/admin" class="text-purple-600 hover:text-purple-800 font-semibold">Admin Panel</a>
                    {% endif %}
                    <a href="/logout" class="text-red-600 hover:text-red-800">Logout</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Total Sessions</h3>
                <p class="text-3xl font-bold text-indigo-600">{{ recent_sessions|length }}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Modules Completed</h3>
                <p class="text-3xl font-bold text-green-600">{{ progress|selectattr('completed')|list|length }}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Fellowship Year</h3>
                <p class="text-3xl font-bold text-purple-600">{{ user.fellowship_year or 'N/A' }}</p>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Recent Sessions</h2>
            {% if recent_sessions %}
            <div class="space-y-4">
                {% for session in recent_sessions %}
                <div class="border-l-4 border-indigo-500 pl-4 py-2">
                    <h3 class="font-semibold text-gray-900">{{ session.module_name or session.session_type }}</h3>
                    <p class="text-sm text-gray-600">{{ session.started_at.strftime('%Y-%m-%d %H:%M') }}</p>
                    <p class="text-sm text-gray-500">Model: {{ session.model_used }}</p>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-gray-600">No sessions yet. Start training!</p>
            {% endif %}
        </div>

        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Quick Links</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a href="/local_models.html" class="group block p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-300 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-bold text-lg text-blue-900 group-hover:text-blue-600">ASP Response Tuning</h3>
                        <span class="text-2xl group-hover:scale-110 transition-transform">🤖</span>
                    </div>
                    <p class="text-sm text-blue-700">Compare AI Models and Evidence Enhancement</p>
                </a>
                <a href="/asp_ai_agent.html" class="group block p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-300 rounded-lg hover:border-purple-500 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-bold text-lg text-purple-900 group-hover:text-purple-600">AI Chat Assistant</h3>
                        <span class="text-2xl group-hover:scale-110 transition-transform">💬</span>
                    </div>
                    <p class="text-sm text-purple-700">General ASP training and Q&A</p>
                </a>
                <a href="/agent_models.html" class="group block p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 border-2 border-indigo-300 rounded-lg hover:border-indigo-500 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-bold text-lg text-indigo-900 group-hover:text-indigo-600">ASP Leadership Lab</h3>
                        <span class="text-2xl group-hover:scale-110 transition-transform">📊</span>
                    </div>
                    <p class="text-sm text-indigo-700">Business Case & Prescriber Psychology modules</p>
                </a>
                <a href="/cicu_module.html" class="group block p-6 bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300 rounded-lg hover:border-green-500 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-bold text-lg text-green-900 group-hover:text-green-600">CICU Training Module</h3>
                        <span class="text-2xl group-hover:scale-110 transition-transform">🏥</span>
                    </div>
                    <p class="text-sm text-green-700">Critical care antimicrobial stewardship scenarios</p>
                </a>
            </div>
        </div>

        <!-- Privacy Notice -->
        <div class="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
            <h3 class="text-sm font-bold text-blue-900 mb-2">🔒 Privacy Notice</h3>
            <p class="text-sm text-blue-800">
                <strong>What is not stored:</strong> Chat histories are not stored, nor are any responses submitted to questions in the training modules.
            </p>
            <p class="text-sm text-blue-800 mt-2">
                <strong>What is stored:</strong> Your progress through the ASP curriculum and scores achieved on each module
                are saved in the ASP AI Agent database to track your learning journey. You may retake any module at any time,
                which will update your previous scores for that module.
            </p>
        </div>
    </div>
</body>
</html>
'''

VERIFICATION_PENDING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-lg w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">📧</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">
                {% if resent %}
                Verification Email Sent!
                {% else %}
                Check Your Email
                {% endif %}
            </h1>

            {% if email_sent %}
            <p class="text-gray-700 mb-6">
                We've sent a verification link to <strong>{{ email }}</strong>
            </p>
            <p class="text-gray-600 mb-4">
                Please check your inbox and click the link to verify your account.
            </p>
            {% else %}
            <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded mb-6">
                <p class="font-semibold mb-2">⚠️ Email System Not Configured</p>
                <p class="text-sm">The verification link has been printed to the server console. Check the terminal where the server is running.</p>
            </div>
            {% endif %}

            <div class="text-sm text-gray-500 mb-6">
                <p>Didn't receive the email?</p>
                <ul class="list-disc list-inside mt-2 text-left">
                    <li>Check your spam/junk folder</li>
                    <li>Make sure {{ email }} is correct</li>
                    <li>Wait a few minutes for the email to arrive</li>
                </ul>
            </div>

            <form method="POST" action="/resend-verification" class="mb-6">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                <input type="hidden" name="email" value="{{ email }}">
                <button type="submit"
                        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition duration-200">
                    Resend Verification Email
                </button>
            </form>

            <a href="/login" class="text-indigo-600 hover:text-indigo-800 text-sm">
                Back to Login
            </a>
        </div>
    </div>
</body>
</html>
'''

VERIFICATION_SUCCESS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verified - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">✅</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">Email Verified!</h1>
            <p class="text-gray-600 mb-6">
                Your email has been successfully verified. You can now sign in to your account.
            </p>
            <a href="https://asp-ai-agent.com/login"
               class="inline-block bg-indigo-600 text-white py-3 px-8 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold">
                Sign In Now
            </a>
        </div>
    </div>
</body>
</html>
'''

VERIFICATION_ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Error - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">❌</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">Verification Failed</h1>
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                {{ error }}
            </div>
            <p class="text-gray-600 mb-6">
                The verification link may be invalid or has already been used.
            </p>
            <a href="/login"
               class="inline-block bg-indigo-600 text-white py-2 px-6 rounded-lg hover:bg-indigo-700 transition duration-200">
                Go to Login
            </a>
        </div>
    </div>
</body>
</html>
'''

VERIFICATION_EXPIRED_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Expired - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">⏰</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">Link Expired</h1>
            <p class="text-gray-600 mb-6">
                This verification link has expired. Verification links are valid for 24 hours.
            </p>
            <p class="text-gray-700 mb-6">
                Click below to receive a new verification email at <strong>{{ email }}</strong>
            </p>
            <form method="POST" action="/resend-verification">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                <input type="hidden" name="user_id" value="{{ user_id }}">
                <button type="submit"
                        class="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold mb-4">
                    Send New Verification Email
                </button>
            </form>
            <a href="/login" class="text-indigo-600 hover:text-indigo-800 text-sm">
                Back to Login
            </a>
        </div>
    </div>
</body>
</html>
'''

VERIFICATION_REQUIRED_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification Required - ASP AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <div class="bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">🔒</div>
            <h1 class="text-2xl font-bold text-gray-900 mb-4">Email Verification Required</h1>
            <p class="text-gray-700 mb-6">
                Please verify your email address before signing in.
            </p>
            <p class="text-gray-600 mb-6">
                Check your inbox at <strong>{{ email }}</strong> for the verification link.
            </p>
            <form method="POST" action="/resend-verification">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                <input type="hidden" name="user_id" value="{{ user_id }}">
                <button type="submit"
                        class="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold mb-4">
                    Resend Verification Email
                </button>
            </form>
            <a href="/login" class="text-indigo-600 hover:text-indigo-800 text-sm">
                Back to Login
            </a>
        </div>
    </div>
</body>
</html>
'''


# ============================================================
# ADMIN ROUTES
# ============================================================

@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard for user management"""
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE)


@auth_bp.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_list_users():
    """Get all users with their activity stats"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    user_data = []
    for user in users:
        # Get session count
        session_count = UserSession.query.filter_by(user_id=user.id).count()
        
        # Get last session
        last_session = UserSession.query.filter_by(user_id=user.id)\
            .order_by(UserSession.started_at.desc()).first()
        
        # Get progress count
        progress_count = UserProgress.query.filter_by(user_id=user.id).count()
        completed_count = UserProgress.query.filter_by(
            user_id=user.id, completed=True
        ).count()
        
        user_data.append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'institution': user.institution,
            'fellowship_year': user.fellowship_year,
            'specialty': user.specialty,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'session_count': session_count,
            'last_session': last_session.started_at.isoformat() if last_session else None,
            'modules_started': progress_count,
            'modules_completed': completed_count
        })
    
    return jsonify({
        'users': user_data,
        'total': len(user_data)
    })


@auth_bp.route('/api/admin/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def admin_get_user(user_id):
    """Get detailed information about a specific user"""
    user = User.query.get_or_404(user_id)
    
    # Get recent sessions
    recent_sessions = UserSession.query.filter_by(user_id=user_id)\
        .order_by(UserSession.started_at.desc()).limit(10).all()
    
    # Get progress
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': user.to_dict(),
        'recent_sessions': [s.to_dict() for s in recent_sessions],
        'progress': [p.to_dict() for p in progress]
    })


@auth_bp.route('/api/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_active(user_id):
    """Toggle user active status (block/unblock)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent blocking yourself
    if user.id == current_user.id:
        return jsonify({
            'success': False,
            'error': 'You cannot block yourself'
        }), 400
    
    # Prevent blocking other admins
    if user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Cannot block admin users'
        }), 400
    
    # Toggle active status
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'is_active': user.is_active,
        'message': f"User {'activated' if user.is_active else 'deactivated'} successfully"
    })


@auth_bp.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user and all their data"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        return jsonify({
            'success': False,
            'error': 'You cannot delete yourself'
        }), 400
    
    # Prevent deleting other admins
    if user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Cannot delete admin users'
        }), 400
    
    email = user.email
    
    # Delete user (cascade will handle related records)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {email} deleted successfully'
    })


@auth_bp.route('/api/admin/users/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def admin_make_admin(user_id):
    """Promote a user to admin"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({
            'success': False,
            'error': 'User is already an admin'
        }), 400
    
    user.is_admin = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'message': f'{user.email} is now an admin'
    })


@auth_bp.route('/api/admin/stats', methods=['GET'])
@login_required
@admin_required
def admin_stats():
    """Get system statistics"""
    from sqlalchemy import func
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(email_verified=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # Users created in last 7 days
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    
    # Total sessions
    total_sessions = UserSession.query.count()
    
    # Active users (logged in within last 7 days)
    active_last_week = User.query.filter(
        User.last_login >= week_ago
    ).count() if week_ago else 0
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'admin_users': admin_users,
        'new_users_this_week': new_users_week,
        'total_sessions': total_sessions,
        'active_last_week': active_last_week
    })


