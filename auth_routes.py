"""
Authentication Routes
Handles user login, signup, logout, and session management
"""

from flask import Blueprint, request, jsonify, render_template_string, redirect, url_for, session as flask_session
from flask_login import login_user, logout_user, login_required, current_user
from auth_models import db, User, UserSession, UserProgress
from datetime import datetime
import re

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

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

        db.session.add(user)
        db.session.commit()

        # Auto-login after signup
        login_user(user)
        user.update_last_login()

        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'user': user.to_dict(),
                'redirect': '/dashboard'
            })

        return redirect('/dashboard')

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


# HTML Templates (will be moved to separate files later)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - ASP AI Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
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
    <script src="https://cdn.tailwindcss.com"></script>
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
    <script src="https://cdn.tailwindcss.com"></script>
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
    <script src="https://cdn.tailwindcss.com"></script>
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
    </div>
</body>
</html>
'''
