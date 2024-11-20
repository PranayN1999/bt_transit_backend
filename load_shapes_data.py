import pandas as pd
from sqlalchemy.orm import Session
from models import Shape
from database import engine
from create_tables import create_tables
from envConfig import GTFS_ROOT_FILE_PATH

# Reference: https://dnmtechs.com/loading-csv-file-into-database-using-sqlalchemy-in-python-3/
# Regerence: https://iifx.dev/en/articles/167606266
# Used this for all the load scripts

def load_shapes_data():
  try:
    # Read shapes.txt into a pandas DataFrame
    df = pd.read_csv(GTFS_ROOT_FILE_PATH + '/shapes.txt')

    # Create a new session
    with Session(engine) as session:
      for _, row in df.iterrows():
        shape = Shape(
          shape_id=row['shape_id'],
          shape_pt_lat=row['shape_pt_lat'],
          shape_pt_lon=row['shape_pt_lon'],
          shape_pt_sequence=row['shape_pt_sequence'],
          shape_dist_traveled=row['shape_dist_traveled'] if pd.notna(row['shape_dist_traveled']) else None,
          eta_pattern_id=row['eta_pattern_id'] if pd.notna(row['eta_pattern_id']) else None
        )
        session.add(shape)

      # Commit the session to save the data to the database
      session.commit()

    print("Shapes data loaded successfully.")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  create_tables()
  load_shapes_data()
