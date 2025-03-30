from sqlalchemy import create_engine

# Replace with your actual database credentials
DATABASE_URL=postgresql+psycopg2://postgres:2021UBA9016@localhost:5432/postgres

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("✅ Database connected successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
