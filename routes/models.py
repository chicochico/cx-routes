import datetime
import uuid

from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

# from sqlalchemy import select
from sqlalchemy.sql import text

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
        query = f"""
        select
            st_length(
                st_makeline(coordinates::geometry ORDER BY created_at)::geography
            ) as route_length
        from waypoint
        where route_id = '{str(self.id)}'
        """
        (length,) = db.execute(text(query)).first()
        return length / 1000

    @staticmethod
    def get_longest_route_for_day(db, date):
        """
        Execute query to get route with longest distance
        for a certain date in the past
        """
        query = f"""
        select
            route_id
            ,st_length(
                st_makeline(coordinates::geometry ORDER BY created_at)::geography
            ) as route_length
        from waypoint
        where created_at::date = '{date.isoformat()}'
        group by route_id
        order by route_length desc
        fetch first 1 row only
        """
        route_id, route_length = db.execute(text(query)).one()
        route = db.query(Route).get(route_id)
        route.length_km = route_length / 1000  # in km
        return route


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

    @validates("route")
    def validate_route(self, key, route):
        if not route.created_at.date() == datetime.datetime.utcnow().date():
            raise ValueError(
                "Cannot add waypoint to route because the route is closed."
            )
        else:
            return route
