import pandas as pd
from sqlalchemy.orm import Session
from models import Stop
from database import engine
from create_tables import create_tables
from envConfig import GTFS_ROOT_FILE_PATH

def load_stops_data():
  try:
    # Read stops.txt into a pandas DataFrame
    df = pd.read_csv(GTFS_ROOT_FILE_PATH + '/stops.txt')

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        stop = Stop(
          stop_id=row['stop_id'],
          stop_name=row['stop_name'],
          stop_lat=row['stop_lat'],
          stop_lon=row['stop_lon'],
          stop_code=row['stop_code'] if pd.notna(row['stop_code']) else None,
          stop_desc=row['stop_desc'] if pd.notna(row['stop_desc']) else None,
          zone_id=row['zone_id'] if pd.notna(row['zone_id']) else None,
          stop_url=row['stop_url'] if pd.notna(row['stop_url']) else None,
          location_type=row['location_type'] if pd.notna(row['location_type']) else None,
          parent_station=row['parent_station'] if pd.notna(row['parent_station']) else None,
          stop_timezone=row['stop_timezone'] if pd.notna(row['stop_timezone']) else None,
          wheelchair_boarding=row['wheelchair_boarding'] if pd.notna(row['wheelchair_boarding']) else None,
          eta_station_id=row['eta_station_id'] if pd.notna(row['eta_station_id']) else None
        )
        session.add(stop)

      # Commit the session to save the data to the database
      session.commit()

    print("Stops data loaded successfully.")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_stops_data()
