import datetime
import uuid

from geoalchemy2 import functions as func
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography, Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# from sqlalchemy import select
from sqlalchemy.sql import cast

from routes.db.base_class import Base


class Route(Base):
    __tablename__ = "route"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    waypoints = relationship("Waypoint", order_by="Waypoint.id", back_populates="route")

    def calculate_length_in_km(self, db):
        """
        Execute a query to calculate the route
        length with PostGist functions
        """
        waypoints = (
            db.query(Waypoint.coordinates)
            .where(Waypoint.route_id == self.id)
            .order_by(Waypoint.created_at)
            .subquery()
        )

        (length,) = db.query(
            func.ST_Length(
                cast(
                    func.ST_MakeLine(cast(waypoints.c.coordinates, Geometry)), Geography
                )
            )
        ).first()
        return length / 1000


class Waypoint(Base):
    __tablename__ = "waypoint"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    coordinates = Column(
        Geography(geometry_type="POINT", srid=4326)
    )  # 4326 referst to WSG84
    route_id = Column(UUID(as_uuid=True), ForeignKey("route.id"))
    route = relationship("Route", back_populates="waypoints")

    @property
    def lat(self):
        return to_shape(self.coordinates).x

    @property
    def lon(self):
        return to_shape(self.coordinates).y
