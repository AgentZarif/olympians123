"""
Database initialization and seeding script for Olympus
"""
from app import app, db
from models import User, Course, Question, LiveClass
from services.question_scraper import scraper
from datetime import datetime, timedelta

def init_and_seed():
    with app.app_context():
        # Create all tables
        print("📦 Creating database tables...")
        db.create_all()
        print("✅ Tables created")
        
        # Create admin user
        if not User.query.filter_by(email='admin@olympus.com').first():
            print("👤 Creating admin user...")
            admin = User(email='admin@olympus.com', name='Admin User', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin created: admin@olympus.com / admin123")
        
        # Create student user
        if not User.query.filter_by(email='student@olympus.com').first():
            print("👤 Creating student user...")
            student = User(email='student@olympus.com', name='ছাত্র/ছাত্রী', role='student')
            student.set_password('student123')
            db.session.add(student)
            print("✅ Student created: student@olympus.com / student123")
        
        #Create courses
        courses_data = [
            {
                'title': 'উচ্চতর বীজগণিত (Advanced Algebra)',
                'description': 'অলিম্পিয়াডের জন্য এডভান্স বীজগণিত - সমীকরণ, অসমতা, ফাংশন, এবং পলিনোমিয়াল',
                'instructor_name': 'ড. রহিম আহমেদ (IMO 2018 স্বর্ণপদক)',
                'duration_hours': 24,
                'lesson_count': 18,
                'difficulty': 'advanced',
                'category': 'mathematics'
            },
            {
                'title': 'জ্যামিতির মূলনীতি (Geometry Fundamentals)',
                'description': 'ইউক্লিডীয় জ্যামিতি থেকে আধুনিক জ্যামিতি - ত্রিভুজ, বৃত্ত, বহুভুজ',
                'instructor_name': 'প্রফেসর করিম হোসেন (জাতীয় পদকপ্রাপ্ত)',
                'duration_hours': 20,
                'lesson_count': 15,
                'difficulty': 'intermediate',
                'category': 'mathematics'
            },
            {
                'title': 'সংখ্যাতত্ত্ব (Number Theory)',
                'description': 'ডিভিসিবিলিটি, প্রাইম নাম্বার, মডুলার অ্যারিথমেটিক, ডায়োফ্যান্টাইন সমীকরণ',
                'instructor_name': 'তানভীর হাসান (BdMO 2020 চ্যাম্পিয়ন)',
                'duration_hours': 18,
                'lesson_count': 12,
                'difficulty': 'hard',
                'category': 'mathematics'
            },
            {
                'title': 'কম্বিনেটরিক্স (Combinatorics)',
                'description': 'পারমুটেশন, কম্বিনেশন, গ্রাফ থিওরি, পিজিয়নহোল প্রিন্সিপাল',
                'instructor_name': 'সাদিয়া ইসলাম (AIME কোয়ালিফায়ার)',
                'duration_hours': 16,
                'lesson_count': 10,
                'difficulty': 'medium',
                'category': 'mathematics'
            }
        ]
        
        print("📚 Creating courses...")
        for course_data in courses_data:
            if not Course.query.filter_by(title=course_data['title']).first():
                course = Course(**course_data)
                db.session.add(course)
        print(f"✅ Created {len(courses_data)} courses")
        
        # Add olympiad questions
        print("📝 Adding olympiad questions...")
        questions = scraper.get_sample_bdmo_questions()
        saved = scraper.save_questions_to_db(questions)
        print(f"✅ Added {saved} olympiad questions")
        
        # Create live class
        if not LiveClass.query.first():
            print("🎥 Creating live class...")
            live_class = LiveClass(
                title='উচ্চতর গণিত - ক্যালকুলাসের মূলনীতি',
                description='ডেরিভেটিভ, ইন্টিগ্রেশন, এবং লিমিট - প্রাকটিকাল এপ্লিকেশন সহ',
                instructor_id=1,
                channel_name='olympus_calculus_101',
                scheduled_start=datetime.utcnow() + timedelta(hours=2),
                scheduled_end=datetime.utcnow() + timedelta(hours=3, minutes=30),
                is_live=True
            )
            db.session.add(live_class)
            print("✅ Live class created")
        
        db.session.commit()
        print("\n🎉 Database initialized and seeded successfully!\n")
        print("=" * 50)
        print("Demo Accounts:")
        print("  Admin:   admin@olympus.com / admin123")
        print("  Student: student@olympus.com / student123")
        print("=" * 50)

if __name__ == '__main__':
    init_and_seed()
