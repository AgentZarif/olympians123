"""
Update database with real Olympus courses and move old content to resources
"""
from app import app, db
from models import Course

def update_courses():
    with app.app_context():
        # Delete old math olympiad courses
        Course.query.delete()
        
        # Create 3 actual courses
        courses = [
            {
                'title': 'Primary Problem-Solving Foundations',
                'description': '''A thoughtfully designed 3-month foundation program aimed at building strong, lasting mathematical thinking in young learners.

**What You'll Learn:**
• How to think logically and systematically, not just arrive at answers
• Deep conceptual understanding and pattern recognition
• Structured reasoning and problem-solving strategies

**Course Structure:**
• 3 live classes per week (60 minutes each)
• Ideal for Class 3–5 students
• Weekly short tests for consistency
• Monthly evaluation tests with detailed discussions
• Final Certificate Examination in Month 3
• Performance-based certificates upon completion

**Why This Course:**
• Student-centric approach with clear explanations
• Interactive discussions and guided exploration
• Recorded sessions available for revision
• Continuous doubt-solving and academic support
• Overseen by Olympiad-experienced mentors

This course nurtures confidence, curiosity, logical reasoning, and disciplined thinking—skills that benefit both school academics and future competitive learning.''',
                'instructor_name': 'Olympiad-Experienced Mentors',
                'duration_hours': 72,  # 3 months, 3 classes/week, 1 hour each
                'lesson_count': 36,
                'difficulty': 'beginner',
                'category': 'foundation',
                'image_url': '🎯'  # Icon placeholder
            },
            {
                'title': 'Intermediate Problem Understanding',
                'description': '''Advanced problem-solving course designed for students ready to tackle more complex mathematical challenges.

**Coming Soon** - Full details will be shared shortly.

This intermediate-level program focuses on deeper mathematical concepts and advanced problem-solving techniques for students who have completed foundational training.''',
                'instructor_name': 'Expert Math Educators',
                'duration_hours': 96,
                'lesson_count': 48,
                'difficulty': 'intermediate',
                'category': 'intermediate',
                'image_url': '📊'
            },
            {
                'title': 'Advanced Math Accelerator',
                'description': '''Elite-level mathematical training for students targeting national and international olympiad competitions.

**Coming Soon** - Full details will be shared shortly.

This advanced program is designed for serious olympiad aspirants, focusing on competition-level problem-solving and mathematical creativity.''',
                'instructor_name': 'National Olympiad Champions',
                'duration_hours': 120,
                'lesson_count': 60,
                'difficulty': 'advanced',
                'category': 'olympiad',
                'image_url': '🏆'
            }
        ]
        
        for course_data in courses:
            course = Course(**course_data)
            db.session.add(course)
        
        db.session.commit()
        print("✅ Updated courses successfully!")
        print(f"   • Primary Problem-Solving Foundations")
        print(f"   • Intermediate Problem Understanding")
        print(f"   • Advanced Math Accelerator")

if __name__ == '__main__':
    update_courses()
