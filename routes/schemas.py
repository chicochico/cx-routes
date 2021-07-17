import uuid
from typing import List

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float

    class Config:
        orm_mode = True


class Waypoint(Coordinates):
    route_id: uuid.UUID

    class Config:
        orm_mode = True


class Route(BaseModel):
    id: uuid.UUID
    waypoints: List[Coordinates] = []

    class Config:
        orm_mode = True


class RouteLength(BaseModel):
    route_id: uuid.UUID
    km: float
