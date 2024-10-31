import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Route, Stop, Shape, Trip, StopTime
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

@app.get("/")
async def root():
  try:
    return {"message": "Hello World"}
  except Exception as e:
    logger.error(f"Error in root endpoint: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")

# API to get all routes
@app.get("/routes")
def get_routes(db: Session = Depends(get_db)):
  try:
    routes = db.query(Route).all()
    return routes
  except Exception as e:
    logger.error(f"Error fetching routes: {e}")
    return {"error": "Failed to retrieve routes"}

# API to get a specific route by its ID
@app.get("/routes/{route_id}")
def get_route(route_id: str, db: Session = Depends(get_db)):
  try:
    route = db.query(Route).filter(Route.route_id == route_id).first()
    if route is None:
      raise HTTPException(status_code=404, detail="Route not found")
    return route
  except Exception as e:
    logger.error(f"Error fetching route {route_id}: {e}")
    return {"error": "Failed to retrieve route"}

# API to get stops for a specific route
@app.get("/stops")
def get_stops(db: Session = Depends(get_db)):
  try:
    stops = db.query(Stop).all()
    return stops
  except Exception as e:
    logger.error(f"Error fetching stops: {e}")
    return {"error": "Failed to retrieve stops"}

@app.get("/routes/{route_id}/details")
def get_route_details(route_id: str, db: Session = Depends(get_db)):
  try:
    # Get the route details
    route = db.query(Route).filter(Route.route_id == route_id).first()

    if route is None:
      raise HTTPException(status_code=404, detail="Route not found")
  
    # Get the shape_id for the route from the trips table
    trip = db.query(Trip).filter(Trip.route_id == route_id).first()
    if trip is None:
      raise HTTPException(status_code=404, detail="Trip not found for this route")
    
    shape_id = trip.shape_id
    
    # Get the shape data (coordinates) for the route
    shape = db.query(Shape).filter(Shape.shape_id == shape_id).all()
    shape_coordinates = [{"latitude": s.shape_pt_lat, "longitude": s.shape_pt_lon} for s in shape]
    
    # Get the stop_ids from stop_times using the trip_id
    stop_times = db.query(StopTime).filter(StopTime.trip_id == trip.trip_id).all()
    stop_ids = [st.stop_id for st in stop_times]

    # Get the stop details using stop_ids
    stops = db.query(Stop).filter(Stop.stop_id.in_(stop_ids)).all()
    stop_coordinates = [{"latitude": stop.stop_lat, "longitude": stop.stop_lon, "name": stop.stop_name} for stop in stops]
    
    return {
      "route": route,
      "shape": shape_coordinates,
      "stops": stop_coordinates
    }
  except Exception as e:
    logger.error(f"Error fetching route details for {route_id}: {e}")
    return {"error": "Failed to retrieve route details"}

