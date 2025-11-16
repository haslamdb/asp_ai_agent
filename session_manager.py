#!/usr/bin/env python3
"""
Session Management System for ASP AI Agent
Provides persistent user sessions, progress tracking, and multi-turn conversations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import json
import sqlite3
import hashlib
from dataclasses import dataclass, asdict, field
from enum import Enum
import os

# Database configuration
# Use persistent storage directory in production (AWS EFS mount point)
DEFAULT_DB_PATH = '/var/app/current/data/asp_sessions.db' if os.path.exists('/var/app/current/data') else 'asp_sessions.db'
DB_PATH = os.environ.get('ASP_DB_PATH', DEFAULT_DB_PATH)

class ModuleStatus(Enum):
    """Status for module completion"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_IMPROVEMENT = "needs_improvement"

class DifficultyLevel(Enum):
    """Adaptive difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_message: str = ""
    ai_response: str = ""
    module_id: str = ""
    context_used: Dict = field(default_factory=dict)
    citations: List[Dict] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

@dataclass
class ModuleProgress:
    """Track progress for a specific module"""
    module_id: str
    status: ModuleStatus = ModuleStatus.NOT_STARTED
    attempts: int = 0
    best_score: float = 0.0
    last_attempt: Optional[datetime] = None
    feedback_history: List[Dict] = field(default_factory=list)
    mastery_level: float = 0.0  # 0-1 scale
    time_spent_seconds: float = 0.0

@dataclass
class UserSession:
    """Main session object for tracking user progress"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    email: Optional[str] = None
    name: Optional[str] = None
    institution: Optional[str] = None
    fellowship_year: Optional[int] = None
    
    # Learning state
    current_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    module_progress: Dict[str, ModuleProgress] = field(default_factory=dict)
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    
    # Adaptive learning parameters
    learning_velocity: float = 1.0  # How fast they're progressing
    strength_areas: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    
    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn to history"""
        self.conversation_history.append(turn)
        self.last_active = datetime.now()
        
        # Keep only last 50 turns for memory efficiency
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_context_window(self, num_turns: int = 5) -> List[ConversationTurn]:
        """Get recent conversation context"""
        return self.conversation_history[-num_turns:] if self.conversation_history else []
    
    def update_module_progress(self, module_id: str, score: float, feedback: Dict):
        """Update progress for a module"""
        if module_id not in self.module_progress:
            self.module_progress[module_id] = ModuleProgress(module_id=module_id)
        
        progress = self.module_progress[module_id]
        progress.attempts += 1
        progress.last_attempt = datetime.now()
        progress.best_score = max(progress.best_score, score)
        progress.feedback_history.append({
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'feedback': feedback
        })
        
        # Update status based on score
        if score >= 0.8:
            progress.status = ModuleStatus.COMPLETED
            progress.mastery_level = score
        elif score >= 0.6:
            progress.status = ModuleStatus.IN_PROGRESS
            progress.mastery_level = score
        else:
            progress.status = ModuleStatus.NEEDS_IMPROVEMENT
            progress.mastery_level = score
        
        # Update difficulty based on performance
        self._adjust_difficulty(score)
    
    def _adjust_difficulty(self, recent_score: float):
        """Adjust difficulty based on performance"""
        if recent_score >= 0.85 and self.current_difficulty != DifficultyLevel.EXPERT:
            # Move up
            levels = list(DifficultyLevel)
            current_idx = levels.index(self.current_difficulty)
            if current_idx < len(levels) - 1:
                self.current_difficulty = levels[current_idx + 1]
                self.learning_velocity *= 1.1  # Learning faster
        elif recent_score < 0.5 and self.current_difficulty != DifficultyLevel.BEGINNER:
            # Move down
            levels = list(DifficultyLevel)
            current_idx = levels.index(self.current_difficulty)
            if current_idx > 0:
                self.current_difficulty = levels[current_idx - 1]
                self.learning_velocity *= 0.9  # Slow down
    
    def get_progress_summary(self) -> Dict:
        """Generate a progress summary"""
        completed = sum(1 for p in self.module_progress.values() 
                       if p.status == ModuleStatus.COMPLETED)
        in_progress = sum(1 for p in self.module_progress.values() 
                         if p.status == ModuleStatus.IN_PROGRESS)
        
        avg_mastery = sum(p.mastery_level for p in self.module_progress.values()) / len(self.module_progress) \
                     if self.module_progress else 0
        
        total_time = sum(p.time_spent_seconds for p in self.module_progress.values())
        
        return {
            'user_id': self.user_id,
            'name': self.name,
            'institution': self.institution,
            'fellowship_year': self.fellowship_year,
            'modules_completed': completed,
            'modules_in_progress': in_progress,
            'average_mastery': round(avg_mastery, 2),
            'current_difficulty': self.current_difficulty.value,
            'learning_velocity': round(self.learning_velocity, 2),
            'total_time_hours': round(total_time / 3600, 1),
            'last_active': self.last_active.isoformat(),
            'strength_areas': self.strength_areas,
            'improvement_areas': self.improvement_areas
        }

class SessionManager:
    """Manages all user sessions with database persistence"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.sessions: Dict[str, UserSession] = {}
        self._init_database()
        self._load_active_sessions()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id TEXT PRIMARY KEY,
                email TEXT,
                name TEXT,
                institution TEXT,
                fellowship_year INTEGER,
                created_at TEXT,
                last_active TEXT,
                current_difficulty TEXT,
                learning_velocity REAL,
                session_data TEXT
            )
        ''')
        
        # Create conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                turn_id TEXT PRIMARY KEY,
                user_id TEXT,
                timestamp TEXT,
                module_id TEXT,
                user_message TEXT,
                ai_response TEXT,
                context_used TEXT,
                citations TEXT,
                metrics TEXT,
                FOREIGN KEY (user_id) REFERENCES sessions (user_id)
            )
        ''')
        
        # Create module progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                module_id TEXT,
                status TEXT,
                attempts INTEGER,
                best_score REAL,
                last_attempt TEXT,
                mastery_level REAL,
                time_spent_seconds REAL,
                feedback_history TEXT,
                FOREIGN KEY (user_id) REFERENCES sessions (user_id),
                UNIQUE(user_id, module_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_active_sessions(self):
        """Load recently active sessions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load sessions active in last 7 days
        cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT user_id, session_data FROM sessions 
            WHERE last_active > ? 
            ORDER BY last_active DESC 
            LIMIT 100
        ''', (cutoff_date,))
        
        for row in cursor.fetchall():
            user_id, session_data = row
            try:
                # Deserialize session
                data = json.loads(session_data)
                session = UserSession(user_id=user_id)
                # Restore session state
                for key, value in data.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                self.sessions[user_id] = session
            except Exception as e:
                print(f"Error loading session {user_id}: {str(e)}")
        
        conn.close()
    
    def create_session(self, email: Optional[str] = None, 
                      name: Optional[str] = None,
                      institution: Optional[str] = None,
                      fellowship_year: Optional[int] = None) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            email=email,
            name=name,
            institution=institution,
            fellowship_year=fellowship_year
        )
        self.sessions[session.user_id] = session
        self._save_session(session)
        return session
    
    def get_session(self, user_id: str) -> Optional[UserSession]:
        """Retrieve a session by user ID"""
        if user_id in self.sessions:
            return self.sessions[user_id]
        
        # Try to load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT session_data FROM sessions WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                data = json.loads(row[0])
                session = UserSession(user_id=user_id)
                for key, value in data.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                self.sessions[user_id] = session
                return session
            except Exception as e:
                print(f"Error loading session {user_id}: {str(e)}")
        
        return None
    
    def _save_session(self, session: UserSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize session data
        session_data = json.dumps({
            'current_difficulty': session.current_difficulty.value,
            'learning_velocity': session.learning_velocity,
            'strength_areas': session.strength_areas,
            'improvement_areas': session.improvement_areas
        })
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (user_id, email, name, institution, fellowship_year, 
             created_at, last_active, current_difficulty, 
             learning_velocity, session_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.user_id, session.email, session.name,
            session.institution, session.fellowship_year,
            session.created_at.isoformat(), session.last_active.isoformat(),
            session.current_difficulty.value, session.learning_velocity,
            session_data
        ))
        
        # Save module progress
        for module_id, progress in session.module_progress.items():
            cursor.execute('''
                INSERT OR REPLACE INTO module_progress
                (user_id, module_id, status, attempts, best_score, 
                 last_attempt, mastery_level, time_spent_seconds, feedback_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.user_id, module_id, progress.status.value,
                progress.attempts, progress.best_score,
                progress.last_attempt.isoformat() if progress.last_attempt else None,
                progress.mastery_level, progress.time_spent_seconds,
                json.dumps(progress.feedback_history)
            ))
        
        conn.commit()
        conn.close()
    
    def save_conversation_turn(self, user_id: str, turn: ConversationTurn):
        """Save a conversation turn to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_history
            (turn_id, user_id, timestamp, module_id, user_message, 
             ai_response, context_used, citations, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            turn.turn_id, user_id, turn.timestamp.isoformat(),
            turn.module_id, turn.user_message, turn.ai_response,
            json.dumps(turn.context_used), json.dumps(turn.citations),
            json.dumps(turn.metrics)
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[ConversationTurn]:
        """Get recent conversation history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT turn_id, timestamp, module_id, user_message, 
                   ai_response, context_used, citations, metrics
            FROM conversation_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        turns = []
        for row in cursor.fetchall():
            turn = ConversationTurn(
                turn_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                module_id=row[2],
                user_message=row[3],
                ai_response=row[4],
                context_used=json.loads(row[5]) if row[5] else {},
                citations=json.loads(row[6]) if row[6] else [],
                metrics=json.loads(row[7]) if row[7] else {}
            )
            turns.append(turn)
        
        conn.close()
        return list(reversed(turns))  # Return in chronological order
    
    def update_session(self, session: UserSession):
        """Update an existing session"""
        self.sessions[session.user_id] = session
        self._save_session(session)
    
    def get_analytics(self) -> Dict:
        """Get system-wide analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_users = cursor.fetchone()[0]
        
        # Active users (last 7 days)
        cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE last_active > ?', (cutoff_date,))
        active_users = cursor.fetchone()[0]
        
        # Module completion stats
        cursor.execute('''
            SELECT module_id, 
                   COUNT(DISTINCT user_id) as users,
                   AVG(best_score) as avg_score,
                   SUM(attempts) as total_attempts
            FROM module_progress
            GROUP BY module_id
        ''')
        
        module_stats = {}
        for row in cursor.fetchall():
            module_stats[row[0]] = {
                'users': row[1],
                'avg_score': round(row[2], 2) if row[2] else 0,
                'total_attempts': row[3]
            }
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users_7d': active_users,
            'module_stats': module_stats
        }

# Initialize global session manager
session_manager = SessionManager()