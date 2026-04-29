import os
from dotenv import load_dotenv

from services.email.database import init_db, engine
from services.email.database import Base

# Import all models to ensure they are registered with Base
from services.email import models as email_models
from services.auth import models as auth_models
from services.payment import models as payment_models

def main():
    load_dotenv()
    print("Database URL:", os.getenv("SUPABASE_DATABASE_URL")[:30] + "...")
    print("Migrating Database tables...")
    Base.metadata.create_all(bind=engine)
    
    from services.email.database import SessionLocal
    with SessionLocal() as db:
        if db.query(payment_models.Plan).count() == 0:
            print("Seeding default plans...")
            plans = [
                payment_models.Plan(name="Basic", price_inr=0, max_contacts=10, max_emails=10, max_campaigns=0),
                payment_models.Plan(name="Standard", price_inr=999, max_contacts=20, max_emails=20, max_campaigns=2),
                payment_models.Plan(name="Premium", price_inr=1999, max_contacts=40, max_emails=40, max_campaigns=5),
            ]
            db.add_all(plans)
            db.commit()
            
    print("Done!")

if __name__ == "__main__":
    main()
