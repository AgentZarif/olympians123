"""
Teacher/Admin Panel Route
"""
from flask import render_template, session, redirect, url_for, flash
from app import app, db
from models import User, Course, Question, LiveClass, ChatMessage

@app.route('/teacher')
def teacher_panel():
    """Teacher/Admin panel - separate from student dashboard"""
    if 'user' not in session:
        flash('লগইন করুন', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user']['id'])
    
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
                         recent_messages=recent_messages,
                         user=user)

# Add this to app.py by importing this file
