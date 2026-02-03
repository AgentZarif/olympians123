"""
Olympus - Math Olympiad Learning Platform
Production version with database, AI tutor, and real content
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import config
from models import db, migrate, User, Course, Question, Exam, Submission, ChatMessage, LiveClass
# Import Gemini lazily to avoid Python 3.14 compatibility issues at startup
# from services.gemini_tutor import gemini_tutor
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Context processor for templates
@app.context_processor
def inject_user():
    return dict(user=session.get('user'))

# ============================================================================
# HOMEPAGE & PUBLIC ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user'] = user.to_dict()
            flash(f'স্বাগতম, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('ভুল ইমেইল বা পাসওয়ার্ড', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get and sanitize form data
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        nickname = request.form.get('nickname', '').strip() or None
        mobile_number = request.form.get('mobile_number', '').strip()
        class_level = request.form.get('class_level', '').strip()
        school_name = request.form.get('school_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([email, name, mobile_number, class_level, school_name, password]):
            flash('সকল প্রয়োজনীয় তথ্য পূরণ করুন', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('পাসওয়ার্ড মিলছে না', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('পাসওয়ার্ড কমপক্ষে ৬ অক্ষর হতে হবে', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('এই ইমেইল ইতিমধ্যে ব্যবহৃত হয়েছে', 'danger')
            return render_template('register.html')
        
        # Create new user with all fields
        new_user = User(
            email=email,
            name=name,
            nickname=nickname,
            mobile_number=mobile_number,  # TODO: Encrypt in production
            class_level=class_level,
            school_name=school_name,
            role='student'
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'অভিনন্দন, {name}! আপনার অ্যাকাউন্ট তৈরি হয়েছে', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('লগআউট সফল', 'info')
    return redirect(url_for('index'))

# ============================================================================
# PROTECTED ROUTES
# ============================================================================

def login_required(f):
    """Decorator to check if user is logged in"""
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash('লগইন করুন', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    # Redirect teachers/admins to teacher panel
    if user.role in ['teacher', 'admin']:
        return redirect(url_for('teacher_panel'))
    
    # Student dashboard
    submissions = Submission.query.filter_by(user_id=user_id).all()
    avg_score = sum([s.score for s in submissions]) / len(submissions) if submissions else 0
    
    stats = {
        'enrolled_courses': Course.query.filter_by(is_published=True).count(),
        'completed_exams': len(submissions),
        'learning_hours': len(submissions) * 1.5,
        'avg_score': int(avg_score)
    }
    
    upcoming_classes = LiveClass.query.filter(
        LiveClass.scheduled_start > datetime.utcnow()
    ).order_by(LiveClass.scheduled_start).limit(5).all()
    
    # Get recent submissions for activity feed
    recent_submissions = Submission.query.filter_by(user_id=user_id).order_by(Submission.submitted_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, upcoming_classes=upcoming_classes, recent_submissions=recent_submissions)

@app.route('/courses')
def courses():
    """Courses are publicly accessible in guest mode"""
    all_courses = Course.query.filter_by(is_published=True).all()
    return render_template('courses.html', courses=all_courses)

@app.route('/exams')
@login_required
def exams():
    user_id = session['user']['id']
    
    # Get upcoming exams
    upcoming_exams = Exam.query.filter(
        Exam.is_published == True,
        Exam.scheduled_date > datetime.utcnow()
    ).order_by(Exam.scheduled_date).all()
    
    # Get completed exams
    completed_submissions = Submission.query.filter_by(user_id=user_id).all()
    exam_ids = [s.exam_id for s in completed_submissions]
    completed_exams = Exam.query.filter(Exam.id.in_(exam_ids)).all() if exam_ids else []
    
    return render_template('exams.html', 
                         upcoming_exams=upcoming_exams,
                         completed_exams=completed_exams,
                         submissions={s.exam_id: s for s in completed_submissions})

@app.route('/questions')
@login_required
def questions():
    # Get all olympiad questions
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')
    
    query = Question.query
    if topic:
        query = query.filter_by(topic=topic)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    all_questions = query.order_by(Question.created_at.desc()).all()
    topics = db.session.query(Question.topic).distinct().all()
    
    return render_template('questions.html', 
                         questions=all_questions, 
                         topics=[t[0] for t in topics])

@app.route('/classes')
@login_required
def classes():
    # Get current or next live class
    current_class = LiveClass.query.filter_by(is_live=True).first()
    
    if not current_class:
        # Get next scheduled class
        current_class = LiveClass.query.filter(
            LiveClass.scheduled_start > datetime.utcnow()
        ).order_by(LiveClass.scheduled_start).first()
    
    return render_template('classes.html', live_class=current_class)

@app.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

@app.route('/teacher')
@login_required
def teacher_panel():
    """Teacher/Admin panel - separate from student dashboard"""
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    if user.role not in ['teacher', 'admin']:
        flash('এই পেজে প্রবেশের অনুমতি নেই', 'danger')
        return redirect(url_for('dashboard'))
    
    # Teacher/Admin statistics
    stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_courses': Course.query.count(),
        'total_questions': Question.query.count(),
        'active_classes': LiveClass.query.filter_by(is_live=True).count()
    }
    
    # Recent activity
    recent_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5).all()
    recent_messages = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    return render_template('teacher_panel.html', 
                         stats=stats,
                         recent_students=recent_students,
                         recent_messages=recent_messages)

# ============================================================================
# AI TUTOR
# ============================================================================

@app.route('/ai_chat')
@login_required
def ai_chat():
    """AI Chat is a locked feature - requires login"""
    return render_template('ai_chat.html')

@app.route('/api/ai/ask', methods=['POST'])
@login_required
def ai_ask():
    """AI Chat API - requires authentication"""
    # Lazy import to avoid Python 3.14 startup issues
    try:
        from services.gemini_tutor import gemini_tutor
    except Exception as e:
        return jsonify({
            'error': f'AI টিউটর লোড করতে সমস্যা হয়েছে। Error: {str(e)}',
            'details': 'Gemini API initialization failed. Please check API key and Python version compatibility.'
        }), 500
    
    data = request.get_json()
    question = data.get('message', '')
    context = data.get('context', [])
    
    if not question:
        return jsonify({'error': 'প্রশ্ন লিখুন'}), 400
    
    # Get response from Gemini
    try:
        response = gemini_tutor.ask(question, context)
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': 'AI টিউটর রেসপন্স দিতে ব্যর্থ হয়েছে',
            'details': str(e)
        }), 500

# ============================================================================
# LIVE CLASS CHAT API
# ============================================================================

@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    class_id = request.args.get('class_id')
    
    if class_id:
        messages = ChatMessage.query.filter_by(live_class_id=int(class_id)).order_by(ChatMessage.created_at).all()
    else:
        # Get latest class messages
        latest_class = LiveClass.query.filter_by(is_live=True).first()
        if latest_class:
            messages = ChatMessage.query.filter_by(live_class_id=latest_class.id).order_by(ChatMessage.created_at).all()
        else:
            messages = []
    
    return jsonify([msg.to_dict() for msg in messages])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    data = request.get_json()
    message_text = data.get('message', '')
    class_id = data.get('class_id')
    
    if not message_text:
        return jsonify({'error': 'Message required'}), 400
    
    user_id = session['user']['id']
    
    # Get or create current live class
    if class_id:
        live_class = LiveClass.query.get(class_id)
    else:
        live_class = LiveClass.query.filter_by(is_live=True).first()
    
    msg = ChatMessage(
        user_id=user_id,
        live_class_id=live_class.id if live_class else None,
        message=message_text
    )
    db.session.add(msg)
    db.session.commit()
    
    return jsonify(msg.to_dict())

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ============================================================================
# CLI COMMANDS
# ============================================================================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("✅ Database initialized")

@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    from services.question_scraper import scraper
    
    # Create admin user
    if not User.query.filter_by(email='admin@olympus.com').first():
        admin = User(email='admin@olympus.com', name='Admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create sample courses
    courses_data = [
        {
            'title': 'উচ্চতর বীজগণিত',
            'description': 'অলিম্পিয়াডের জন্য এডভান্স বীজগণিত - সমীকরণ, অসমতা, ফাংশন',
            'instructor_name': 'ড. রহিম আহমেদ',
            'duration_hours': 24,
            'lesson_count': 18,
            'difficulty': 'advanced',
            'category': 'mathematics'
        },
        {
            'title': 'জ্যামিতির মূলনীতি',
            'description': 'ইউক্লিডীয় জ্যামিতি থেকে আধুনিক জ্যামিতি - ত্রিভুজ, বৃত্ত, বহুভুজ',
            'instructor_name': 'প্রফেসর করিম হোসেন',
            'duration_hours': 20,
            'lesson_count': 15,
            'difficulty': 'intermediate',
            'category': 'mathematics'
        }
    ]
    
    for course_data in courses_data:
        if not Course.query.filter_by(title=course_data['title']).first():
            course = Course(**course_data)
            db.session.add(course)
    
    # Add olympiad questions
    questions = scraper.get_sample_bdmo_questions()
    scraper.save_questions_to_db(questions)
    
    # Create a live class
    if not LiveClass.query.first():
        from datetime import timedelta
        live_class = LiveClass(
            title='উচ্চতর গণিত - ক্যালকুলাসের মূলনীতি',
            description='ক্যালকুলাসের বেসিক থেকে এডভান্স',
            instructor_id=1,
            channel_name='olympus_math_101',
            scheduled_start=datetime.utcnow() + timedelta(days=1),
            is_live=True
        )
        db.session.add(live_class)
    
    db.session.commit()
    print("✅ Database seeded with sample data")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
