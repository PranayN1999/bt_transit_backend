from models import Base
from database import engine

def create_tables():
  # Create all tables (if they don't exist)
  Base.metadata.create_all(bind=engine)
  print("Tables created successfully.")