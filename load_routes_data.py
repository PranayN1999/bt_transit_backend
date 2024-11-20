import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import engine
from models import Route
from create_tables import create_tables
from envConfig import GTFS_ROOT_FILE_PATH

# Reference: https://dnmtechs.com/loading-csv-file-into-database-using-sqlalchemy-in-python-3/
# Regerence: https://iifx.dev/en/articles/167606266
# Used this for all the load scripts

def load_routes_data():
  try:
    # Read the routes.txt file into a pandas DataFrame
    df = pd.read_csv(GTFS_ROOT_FILE_PATH + '/routes.txt')

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        # Create a Route object for each row
        route = Route(
          route_id=row['route_id'],
          route_short_name=row['route_short_name'],
          route_long_name=row['route_long_name'] if pd.notna(row['route_long_name']) else None,
          route_type=row['route_type'],
          route_color=row['route_color'] if pd.notna(row['route_color']) else None,
          agency_id=row['agency_id'] if pd.notna(row['agency_id']) else None,
          route_desc=row['route_desc'] if pd.notna(row['route_desc']) else None,
          route_url=row['route_url'] if pd.notna(row['route_url']) else None,
          route_text_color=row['route_text_color'] if pd.notna(row['route_text_color']) else None,
          route_sort_order=row['route_sort_order'] if pd.notna(row['route_sort_order']) else None,
          eta_corridor_id=row['eta_corridor_id'] if pd.notna(row['eta_corridor_id']) else None
        )
        # Add the route to the session
        session.add(route)

      # Commit the session to insert the data into the database
      session.commit()

    print("Routes data loaded successfully.")

  except SQLAlchemyError as e:
    print(f"An error occurred while loading routes data: {e}")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_routes_data()
