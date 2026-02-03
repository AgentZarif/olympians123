"""
Fix authentication and update user passwords with proper hashing
"""
from app import app, db
from models import User

def fix_passwords():
    with app.app_context():
        # Get all users and rehash passwords
        users = [
            {'email': 'admin@olympus.com', 'password': 'admin123', 'name': 'Admin', 'role': 'admin'},
            {'email': 'student@olympus.com', 'password': 'student123', 'name': 'ছাত্র/ছাত্রী', 'role': 'student'}
        ]
        
        for user_data in users:
            user = User.query.filter_by(email=user_data['email']).first()
            if user:
                # Reset password properly
                user.set_password(user_data['password'])
                print(f"✅ Updated password for {user.email}")
            else:
                # Create new user
                user = User(
                    email=user_data['email'],
                    name=user_data['name'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"✅ Created user {user.email}")
        
        db.session.commit()
        print("\n🔐 All passwords updated successfully!")
        print("=" * 50)
        print("Test Accounts:")
        print("  Admin:   admin@olympus.com / admin123")
        print("  Student: student@olympus.com / student123")
        print("=" * 50)

if __name__ == '__main__':
    fix_passwords()
