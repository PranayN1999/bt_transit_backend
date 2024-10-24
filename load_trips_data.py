import pandas as pd
from sqlalchemy.orm import Session
from models import Trip
from database import engine
from create_tables import create_tables

def load_trips_data():
  try:
    # Read trips.txt into a pandas DataFrame
    df = pd.read_csv('C:/Users/prana/Desktop/Cross-Platform/BT_Transit_GTFS_Data/gtfs/trips.txt')

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        trip = Trip(
          route_id=row['route_id'],
          service_id=row['service_id'],
          trip_id=row['trip_id'],
          shape_id=row['shape_id'] if pd.notna(row['shape_id']) else None,
          trip_headsign=row['trip_headsign'] if pd.notna(row['trip_headsign']) else None,
          trip_short_name=row['trip_short_name'] if pd.notna(row['trip_short_name']) else None,
          direction_id=row['direction_id'] if pd.notna(row['direction_id']) else None,
          block_id=row['block_id'] if pd.notna(row['block_id']) else None,
          wheelchair_accessible=row['wheelchair_accessible'] if pd.notna(row['wheelchair_accessible']) else None,
          bikes_allowed=row['bikes_allowed'] if pd.notna(row['bikes_allowed']) else None,
          eta_train_id=row['eta_train_id'] if pd.notna(row['eta_train_id']) else None,
          block_service_id=row['block_service_id'] if pd.notna(row['block_service_id']) else None,
          block_name=row['block_name'] if pd.notna(row['block_name']) else None
        )
        session.add(trip)

      # Commit the session to save the data to the database
      session.commit()

    print("Trips data loaded successfully.")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_trips_data()
