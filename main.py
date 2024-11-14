import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Route, Stop, Shape, Trip, StopTime
from gtfs_realtime_pb2 import FeedMessage
import requests
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from envConfig import GTFS_REAL_TIME_POSITION_UPDATES_URL, GTFS_REAL_TIME_TRIP_UPDATES_URL, GTFS_REAL_TIME_ALERTS_URL
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
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

connected_clients = set()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/routes")
def get_routes(db: Session = Depends(get_db)):
  try:
    routes = db.query(Route).all()
    return routes
  except Exception as e:
    logger.error(f"Error fetching routes: {e}")
    return {"error": "Failed to retrieve routes"}


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


@app.get("/stops")
def get_stops(db: Session = Depends(get_db)):
  try:
    stops = db.query(Stop).all()
    return stops
  except Exception as e:
    logger.error(f"Error fetching stops: {e}")
    return {"error": "Failed to retrieve stops"}
  

@app.get("/all-routes/details")
def get_all_routes_details(db: Session = Depends(get_db)):
    try:
        # Fetch all routes
        routes = db.query(Route).all()
        logger.debug(f"Fetched routes: {routes}")
        
        if not routes:
            logger.debug(f"Fetched routes: {routes}")
            raise HTTPException(status_code=404, detail="No routes found")

        # Collect details for each route
        routes_details = []
        for route in routes:
            # Find the trip associated with the route to get the shape_id
            trip = db.query(Trip).filter(Trip.route_id == route.route_id).first()
            if not trip:
                logger.debug(f"No trip found for route {route.route_id}")
                continue  # Skip if no trip found for this route

            shape_id = trip.shape_id

            # Get shape data for the route
            shape = db.query(Shape).filter(Shape.shape_id == shape_id).all()
            shape_coordinates = [{"latitude": s.shape_pt_lat, "longitude": s.shape_pt_lon} for s in shape]
            logger.debug(f"Shape coordinates for route {route.route_id}: {shape_coordinates}")

            # Get stop_ids from stop_times using the trip_id
            stop_times = db.query(StopTime).filter(StopTime.trip_id == trip.trip_id).all()
            stop_ids = [st.stop_id for st in stop_times]

            # Get stop details using stop_ids
            stops = db.query(Stop).filter(Stop.stop_id.in_(stop_ids)).all()
            stop_coordinates = [{"latitude": stop.stop_lat, "longitude": stop.stop_lon, "name": stop.stop_name} for stop in stops]
            logger.debug(f"Stop coordinates for route {route.route_id}: {stop_coordinates}")

            # Append route details
            routes_details.append({
                "route": route,
                "shape": shape_coordinates,
                "stops": stop_coordinates
            })

        if not routes_details:
            raise HTTPException(status_code=404, detail="No route details found")
        
        return {"routes": routes_details}

    except Exception as e:
        logger.error(f"Error fetching all route details: {e}")
        return {"error": "Failed to retrieve route details"}

async def load_pb_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        feed = FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        logger.error(f"Error loading data from URL {url}: {e}")
        logger.debug(traceback.format_exc())
        return None

async def fetch_bus_positions(db: Session):
    try:
        url = GTFS_REAL_TIME_POSITION_UPDATES_URL
        feed = await load_pb_from_url(url)
        positions = []

        if not feed:
            return {"positions": []}

        for entity in feed.entity:
            if entity.HasField("vehicle"):
                vehicle_id = entity.vehicle.vehicle.id
                trip_id = entity.vehicle.trip.trip_id
                latitude = entity.vehicle.position.latitude
                longitude = entity.vehicle.position.longitude
                bearing = entity.vehicle.position.bearing
                current_stop_sequence = entity.vehicle.current_stop_sequence
                current_status = entity.vehicle.current_status

                # Get route information from trip_id
                trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
                if trip:
                    route = db.query(Route).filter(Route.route_id == trip.route_id).first()
                    if route:
                        positions.append({
                            "vehicle_id": vehicle_id,
                            "trip_id": trip_id,
                            "latitude": latitude,
                            "longitude": longitude,
                            "bearing": bearing,
                            "current_stop_sequence": current_stop_sequence,
                            "current_status": current_status,
                            "route_id": route.route_id,
                            "route_short_name": route.route_short_name,
                            "route_long_name": route.route_long_name,
                            "route_color": route.route_color
                        })
        return {"positions": positions}
    except Exception as e:
        logger.error(f"Error fetching real-time positions: {e}")
        return {"positions": []}

# WebSocket endpoint for real-time bus positions
@app.websocket("/ws/bus-positions")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info("Client connected")

    try:
        while True:
            # Fetch latest bus positions
            bus_positions = await fetch_bus_positions(db)
            if bus_positions:
                message = json.dumps(bus_positions)
                await websocket.send_text(message)
            await asyncio.sleep(2)  # Send updates every 2 seconds
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connected_clients.remove(websocket)

@app.on_event("shutdown")
async def on_shutdown():
    for client in connected_clients:
        await client.close()

@app.get("/real-time-trips")
def get_real_time_trips():
    try:
        url = GTFS_REAL_TIME_TRIP_UPDATES_URL
        feed = load_pb_from_url(url)
        trips = [
            {
                "trip_id": entity.trip_update.trip.trip_id,
                "route_id": entity.trip_update.trip.route_id,
                "start_time": entity.trip_update.trip.start_time,
                "start_date": entity.trip_update.trip.start_date,
                "stop_time_updates": [
                    {
                        "stop_id": update.stop_id,
                        "arrival": update.arrival.time if update.HasField("arrival") else None,
                        "departure": update.departure.time if update.HasField("departure") else None
                    }
                    for update in entity.trip_update.stop_time_update
                ]
            }
            for entity in feed.entity if entity.HasField("trip_update")
        ]
        return {"trips": trips}
    except Exception as e:
        logger.error(f"Error fetching real-time trips: {e}")
        logger.debug(traceback.format_exc())
        return {"error": "Failed to retrieve real-time trips"}

# Real-time Alerts Endpoint
@app.get("/real-time-alerts")
def get_real_time_alerts():
    try:
        url = GTFS_REAL_TIME_ALERTS_URL
        feed = load_pb_from_url(url)
        alerts = [
            {
                "alert_id": entity.id,
                "cause": entity.alert.cause,
                "effect": entity.alert.effect,
                "header_text": entity.alert.header_text.translation[0].text if entity.alert.header_text.translation else None,
                "description_text": entity.alert.description_text.translation[0].text if entity.alert.description_text.translation else None,
                "informed_entity": [
                    {
                        "agency_id": informed.agency_id,
                        "route_id": informed.route_id,
                        "stop_id": informed.stop_id
                    }
                    for informed in entity.alert.informed_entity
                ]
            }
            for entity in feed.entity if entity.HasField("alert")
        ]
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Error fetching real-time alerts: {e}")
        logger.debug(traceback.format_exc())
        return {"error": "Failed to retrieve real-time alerts"}