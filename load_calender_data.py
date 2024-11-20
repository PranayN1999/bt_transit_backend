import pandas as pd
from sqlalchemy.orm import Session
from models import Calendar
from database import engine
from datetime import datetime
from create_tables import create_tables
from envConfig import GTFS_ROOT_FILE_PATH

# Reference: https://dnmtechs.com/loading-csv-file-into-database-using-sqlalchemy-in-python-3/
# Regerence: https://iifx.dev/en/articles/167606266
# Used this for all the load scripts

def load_calendar_data():
  try:
    # Read calendar.txt into a pandas DataFrame
    df = pd.read_csv(GTFS_ROOT_FILE_PATH + '/calendar.txt')

    # Ensure all types are converted to Python-native types
    df = df.astype({
      'monday': 'int',
      'tuesday': 'int',
      'wednesday': 'int',
      'thursday': 'int',
      'friday': 'int',
      'saturday': 'int',
      'sunday': 'int',
    })

    # Function to safely convert dates from float64 to strings and then to dates
    def parse_date(date):
      if pd.notna(date) and isinstance(date, (float, int)):
        return datetime.strptime(str(int(date)), '%Y%m%d').date()
      return None

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        calendar = Calendar(
          service_id=str(int(row['service_id'])) if pd.notna(row['service_id']) else None,
          monday=bool(row['monday']),
          tuesday=bool(row['tuesday']),
          wednesday=bool(row['wednesday']),
          thursday=bool(row['thursday']),
          friday=bool(row['friday']),
          saturday=bool(row['saturday']),
          sunday=bool(row['sunday']),
          start_date=parse_date(row['start_date']),
          end_date=parse_date(row['end_date']),
          service_name=row['service_name'] if pd.notna(row['service_name']) else None,
          eta_schedule_id=str(int(row['eta_schedule_id'])) if pd.notna(row['eta_schedule_id']) else None
        )
        session.add(calendar)

      # Commit the session to save the data to the database
      session.commit()

    print("Calendar data loaded successfully.")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_calendar_data()
