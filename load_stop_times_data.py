import pandas as pd
from sqlalchemy.orm import Session
from models import StopTime
from database import engine
from create_tables import create_tables
from envConfig import GTFS_ROOT_FILE_PATH

def load_stop_times_data():
  try:
    # Read stop_times.txt into a pandas DataFrame
    df = pd.read_csv(GTFS_ROOT_FILE_PATH + '/stop_times.txt')

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        stop_time = StopTime(
          trip_id=row['trip_id'],
          stop_id=row['stop_id'],
          stop_sequence=row['stop_sequence'],
          arrival_time=row['arrival_time'],
          departure_time=row['departure_time'],
          drop_off_type=row['drop_off_type'] if pd.notna(row['drop_off_type']) else None,
          shape_dist_traveled=row['shape_dist_traveled'] if pd.notna(row['shape_dist_traveled']) else None,
          timepoint=row['timepoint'] if pd.notna(row['timepoint']) else None,
          stop_headsign=row['stop_headsign'] if pd.notna(row['stop_headsign']) else None
        )
        session.add(stop_time)

      # Commit the session to save the data to the database
      session.commit()

    print("Stop times data loaded successfully.")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_stop_times_data()
