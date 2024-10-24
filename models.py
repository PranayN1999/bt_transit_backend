from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base

class Agency(Base):
  __tablename__ = 'agency'

  id = Column(Integer, primary_key=True, index=True)
  agency_name = Column(String, nullable=False)
  agency_url = Column(String, nullable=True)
  agency_timezone = Column(String, nullable=False)
  agency_lang = Column(String, nullable=True)
  agency_phone = Column(String, nullable=True)
  agency_fare_url = Column(String, nullable=True)
  agency_email = Column(String, nullable=True)

  routes = relationship("Route", back_populates="agency")


class Route(Base):
  __tablename__ = 'routes'

  route_id = Column(String, primary_key=True, index=True)
  route_short_name = Column(String, nullable=False)
  route_long_name = Column(String, nullable=True)
  route_type = Column(String, nullable=False)
  route_color = Column(String, nullable=True)
  agency_id = Column(Integer, ForeignKey('agency.id'), nullable=True)
  route_desc = Column(String, nullable=True)
  route_url = Column(String, nullable=True)
  route_text_color = Column(String, nullable=True)
  route_sort_order = Column(String, nullable=True)
  eta_corridor_id = Column(Integer, nullable=True)

  agency = relationship("Agency", back_populates="routes")


class Stop(Base):
  __tablename__ = 'stops'

  stop_id = Column(String, primary_key=True, index=True)
  stop_name = Column(String, nullable=False)
  stop_lat = Column(String, nullable=False)
  stop_lon = Column(String, nullable=False)
  stop_code = Column(String, nullable=True)
  stop_desc = Column(String, nullable=True)
  zone_id = Column(String, nullable=True)
  stop_url = Column(String, nullable=True)
  location_type = Column(String, nullable=True)
  parent_station = Column(String, nullable=True)
  stop_timezone = Column(String, nullable=True)
  wheelchair_boarding = Column(String, nullable=True)
  eta_station_id = Column(String, nullable=True)


class StopTime(Base):
  __tablename__ = 'stop_times'

  trip_id = Column(String, primary_key=True, index=True)
  stop_id = Column(String, ForeignKey('stops.stop_id'), primary_key=True)
  stop_sequence = Column(Integer, primary_key=True)
  arrival_time = Column(Time, nullable=False)
  departure_time = Column(Time, nullable=False)
  drop_off_type = Column(Integer, nullable=True)
  shape_dist_traveled = Column(Float, nullable=True)
  timepoint = Column(Integer, nullable=True)
  stop_headsign = Column(String, nullable=True)


class Trip(Base):
  __tablename__ = 'trips'

  route_id = Column(String, ForeignKey('routes.route_id'), nullable=False)
  service_id = Column(String, nullable=False)
  trip_id = Column(String, primary_key=True, index=True)
  shape_id = Column(String, nullable=True)
  trip_headsign = Column(String, nullable=True)
  trip_short_name = Column(String, nullable=True)
  direction_id = Column(String, nullable=True)
  block_id = Column(String, nullable=True)
  wheelchair_accessible = Column(String, nullable=True)
  bikes_allowed = Column(String, nullable=True)
  eta_train_id = Column(String, nullable=True)
  block_service_id = Column(String, nullable=True)
  block_name = Column(String, nullable=True)


class Shape(Base):
  __tablename__ = 'shapes'

  shape_id = Column(String, primary_key=True, index=True)
  shape_pt_lat = Column(String, nullable=False)
  shape_pt_lon = Column(String, nullable=False)
  shape_pt_sequence = Column(Integer, primary_key=True)
  shape_dist_traveled = Column(Float, nullable=True)
  eta_pattern_id = Column(String, nullable=True)


class Calendar(Base):
  __tablename__ = 'calendar'

  service_id = Column(String, primary_key=True, index=True)
  monday = Column(Boolean, nullable=False)
  tuesday = Column(Boolean, nullable=False)
  wednesday = Column(Boolean, nullable=False)
  thursday = Column(Boolean, nullable=False)
  friday = Column(Boolean, nullable=False)
  saturday = Column(Boolean, nullable=False)
  sunday = Column(Boolean, nullable=False)
  start_date = Column(Date, nullable=False)
  end_date = Column(Date, nullable=False)
  service_name = Column(String, nullable=True)
  eta_schedule_id = Column(String, nullable=True)
