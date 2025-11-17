"""
Authentication and User Management Models
Handles user accounts, authentication, and session tracking
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import bcrypt
import json
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile information
    full_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(200))
    fellowship_year = db.Column(db.Integer)  # 1, 2, 3, etc.
    specialty = db.Column(db.String(100))  # ID, Pediatric ID, etc.

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)

    # Email verification
    verification_token = db.Column(db.String(100), unique=True)
    verification_token_expires = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    sessions = db.relationship('UserSession', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def generate_verification_token(self):
        """Generate a new email verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token

    def verify_email(self):
        """Mark email as verified and clear token"""
        self.email_verified = True
        self.verification_token = None
        self.verification_token_expires = None
        db.session.commit()

    def is_verification_token_valid(self, token):
        """Check if verification token is valid and not expired"""
        if not self.verification_token or not self.verification_token_expires:
            return False
        if self.verification_token != token:
            return False
        if datetime.utcnow() > self.verification_token_expires:
            return False
        return True

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'institution': self.institution,
            'fellowship_year': self.fellowship_year,
            'specialty': self.specialty,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class UserSession(db.Model):
    """Track user sessions for progress monitoring"""
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Session metadata
    session_type = db.Column(db.String(50))  # 'business_case', 'prescriber_psychology', 'general_chat'
    module_name = db.Column(db.String(100))

    # Session content
    user_input = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    model_used = db.Column(db.String(50))

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Session metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    session_metadata = db.Column(db.Text)  # JSON string for flexible data storage

    def set_metadata(self, data):
        """Store metadata as JSON"""
        self.session_metadata = json.dumps(data)

    def get_metadata(self):
        """Retrieve metadata from JSON"""
        return json.loads(self.session_metadata) if self.session_metadata else {}

    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'module_name': self.module_name,
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'model_used': self.model_used,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.get_metadata()
        }

    def __repr__(self):
        return f'<UserSession {self.id} - User {self.user_id}>'


class UserProgress(db.Model):
    """Track user progress through modules"""
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Progress tracking
    module_name = db.Column(db.String(100), nullable=False)
    module_type = db.Column(db.String(50))  # 'business_case', 'prescriber_psychology', etc.

    # Completion status
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float)  # Optional scoring
    attempts = db.Column(db.Integer, default=0)

    # Timestamps
    first_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Progress data
    progress_data = db.Column(db.Text)  # JSON for detailed progress tracking

    def set_progress_data(self, data):
        """Store progress data as JSON"""
        self.progress_data = json.dumps(data)

    def get_progress_data(self):
        """Retrieve progress data from JSON"""
        return json.loads(self.progress_data) if self.progress_data else {}

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_name': self.module_name,
            'module_type': self.module_type,
            'completed': self.completed,
            'score': self.score,
            'attempts': self.attempts,
            'first_attempt': self.first_attempt.isoformat() if self.first_attempt else None,
            'last_attempt': self.last_attempt.isoformat() if self.last_attempt else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress_data': self.get_progress_data()
        }

    def __repr__(self):
        return f'<UserProgress {self.module_name} - User {self.user_id}>'
