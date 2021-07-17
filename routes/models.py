import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from routes.db.base_class import Base


class Route(Base):
    __tablename__ = "route"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    waypoints = relationship("Waypoint", order_by="Waypoint.id", back_populates="route")


class Waypoint(Base):
    __tablename__ = "waypoint"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    lat = Column(Float)
    lon = Column(Float)
    route_id = Column(UUID(as_uuid=True), ForeignKey("route.id"))
    route = relationship("Route", back_populates="waypoints")
