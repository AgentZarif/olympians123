"""
Update course icons to use generated images
"""
from app import app, db
from models import Course

def update_icons():
    with app.app_context():
        courses = Course.query.all()
        
        for course in courses:
            if 'Primary' in course.title:
                course.image_url = '/static/images/course_icon_primary_1770129446802.png'
            elif 'Intermediate' in course.title:
                course.image_url = '/static/images/course_icon_intermediate_1770129471350.png'
            elif 'Advanced' in course.title:
                course.image_url = '/static/images/course_icon_advanced_1770129488358.png'
        
        db.session.commit()
        print("✅ Course icons updated successfully!")

if __name__ == '__main__':
    update_icons()
