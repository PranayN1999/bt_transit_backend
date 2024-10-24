from sqlalchemy import Column, Integer, String
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

