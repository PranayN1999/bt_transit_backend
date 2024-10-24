from sqlalchemy import Column, Integer, String, ForeignKey
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