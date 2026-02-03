from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import bcrypt

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    """User model for authentication and profiles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, admin, instructor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor_name = db.Column(db.String(100), nullable=False)
    duration_hours = db.Column(db.Integer, default=0)
    lesson_count = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.String(20), default='intermediate')  # beginner, intermediate, advanced
    category = db.Column(db.String(50), default='mathematics')
    image_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    exams = db.relationship('Exam', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructor_name': self.instructor_name,
            'duration_hours': self.duration_hours,
            'lesson_count': self.lesson_count,
            'difficulty': self.difficulty,
            'category': self.category,
            'image_url': self.image_url
        }

class Question(db.Model):
    """Olympiad question model"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text)
    solution_bangla = db.Column(db.Text)  # Bangla explanation
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    topic = db.Column(db.String(100))  # algebra, geometry, number_theory, combinatorics
    source = db.Column(db.String(100))  # IMO, BdMO, AIME, etc.
    year = db.Column(db.Integer)
    problem_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'problem_statement': self.problem_statement,
            'solution': self.solution,
            'solution_bangla': self.solution_bangla,
            'difficulty': self.difficulty,
            'topic': self.topic,
            'source': self.source,
            'year': self.year,
            'problem_number': self.problem_number
        }

class Exam(db.Model):
    """Exam model"""
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=90)
    total_questions = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Integer, default=60)
    scheduled_date = db.Column(db.DateTime)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'total_questions': self.total_questions,
            'passing_score': self.passing_score,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'is_published': self.is_published
        }

class Submission(db.Model):
    """Exam submission model"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=100)
    answers = db.Column(db.JSON)  # Store answers as JSON
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken_minutes = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'score': self.score,
            'total_score': self.total_score,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_taken_minutes': self.time_taken_minutes
        }

class ChatMessage(db.Model):
    """Live class chat message model"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    live_class_id = db.Column(db.Integer, db.ForeignKey('live_classes.id'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.name if self.user else 'Unknown',
            'role': self.user.role if self.user else 'student',
            'message': self.message,
            'timestamp': self.created_at.strftime('%H:%M') if self.created_at else ''
        }

class LiveClass(db.Model):
    """Live class model"""
    __tablename__ = 'live_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    channel_name = db.Column(db.String(100), unique=True, nullable=False)  # Agora channel
    scheduled_start = db.Column(db.DateTime)
    scheduled_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    recording_url = db.Column(db.String(500))
    is_live = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_messages = db.relationship('ChatMessage', backref='live_class', lazy='dynamic', cascade='all, delete-orphan')
    instructor = db.relationship('User', foreign_keys=[instructor_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructor': self.instructor.name if self.instructor else None,
            'channel_name': self.channel_name,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'is_live': self.is_live
        }
