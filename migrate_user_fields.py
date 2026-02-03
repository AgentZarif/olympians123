"""
Add new fields to User model - migration script
Run this to update existing database
"""
from app import app, db
from models import User

def migrate_user_fields():
    with app.app_context():
        # Add new columns to users table
        try:
            with db.engine.connect() as conn:
                # Check if columns exist, if not add them
                conn.execute(db.text("""
                    ALTER TABLE users ADD COLUMN nickname VARCHAR(50);
                """))
                print("✅ Added nickname column")
        except Exception as e:
            print(f"nickname column may already exist: {e}")
        
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE users ADD COLUMN mobile_number VARCHAR(20);
                """))
                print("✅ Added mobile_number column")
        except Exception as e:
            print(f"mobile_number column may already exist: {e}")
        
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE users ADD COLUMN class_level VARCHAR(20);
                """))
                print("✅ Added class_level column")
        except Exception as e:
            print(f"class_level column may already exist: {e}")
        
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE users ADD COLUMN school_name VARCHAR(200);
                """))
                print("✅ Added school_name column")
        except Exception as e:
            print(f"school_name column may already exist: {e}")
        
        db.session.commit()
        print("\n✅ Database migration completed!")

if __name__ == '__main__':
    migrate_user_fields()
