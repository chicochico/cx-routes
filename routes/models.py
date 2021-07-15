import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from routes.db.base_class import Base


class Route(Base):
    __tablename__ = "route"

    id = Column(String(length=36), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    waypoints = relationship("Coordinates", order_by=created_at, back_populates="route")


class Coordinates(Base):
    __tablename__ = "coordinates"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    lat = Column(Float)
    lon = Column(Float)
    route_id = Column(String, ForeignKey("route.id"))
    route = relationship("Route", back_populates="waypoints")
