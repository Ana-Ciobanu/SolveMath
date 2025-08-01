
from sqlalchemy.orm import Session
from models.models import User
from controllers.controllers import get_password_hash
from db.database import SessionLocal
import os
from dotenv import load_dotenv

load_dotenv()

def create_admin_if_not_exists():
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin")
        admin_user = db.query(User).filter(User.username == admin_username).first()
        if not admin_user:
            admin = User(
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin user '{admin_username}' created successfully.")
        else:
            print(f"Admin user '{admin_username}' already exists.")
    finally:
        db.close()

create_admin_if_not_exists()