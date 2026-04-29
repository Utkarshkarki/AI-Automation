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
    print("Done!")

if __name__ == "__main__":
    main()
