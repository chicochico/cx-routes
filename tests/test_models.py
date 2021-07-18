import datetime as dt
import uuid

import pytest
from geoalchemy2.shape import from_shape
from routes.models import Route, Waypoint
from shapely.geometry import Point


def test_closed_route_validation():
    """
    Test that a waypoint cannot be added to a route that has been closed
    """
    coordinates = from_shape(Point(-25.4025905, -49.3124416))
    route = Route(
        id=uuid.uuid4(), created_at=dt.datetime.utcnow() - dt.timedelta(days=1)
    )
    with pytest.raises(ValueError):
        Waypoint(route=route, coordinates=coordinates)
