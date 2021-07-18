import datetime
import uuid

import ipdb
import pytest
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from routes import crud, models
from routes.api import app
from shapely.geometry import Point

API_ENDPOINT = "http://localhost:8000/"
ROUTE_ENDPOINT = "{}route/".format(API_ENDPOINT)
ROUTE_ADD_WAY_POINT_ENDPOINT = "{}{}/waypoint/".format(ROUTE_ENDPOINT, "{}")
ROUTE_LENGTH_ENDPOINT = "{}{}/length/".format(ROUTE_ENDPOINT, "{}")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def route():
    return models.Route(id=uuid.uuid4(), waypoints=[])


def test_create_route(client, route, monkeypatch):
    def mock_create_route(*args, **kwargs):
        "mock db call"
        return route

    monkeypatch.setattr(crud, "create_route", mock_create_route)
    expected = {"id": str(route.id), "waypoints": []}
    response = client.post(ROUTE_ENDPOINT)
    assert response.status_code == 201
    assert response.json() == expected


def test_create_waypoint(client, route, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        "mock db call"
        return waypoint

    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)
    route_id = str(route.id)
    lat = -25.4025905
    lon = -49.3124416
    point = from_shape(Point(lat, lon), srid=4326)
    waypoint = models.Waypoint(route_id=route_id, coordinates=point)
    expected = {
        "route_id": route_id,
        "lat": waypoint.lat,
        "lon": waypoint.lon,
    }

    response = client.post(
        ROUTE_ADD_WAY_POINT_ENDPOINT.format(route_id), json={"lat": lat, "lon": lon}
    )
    assert response.status_code == 201
    assert response.json() == expected


def test_create_waypoint_invalid_route(client, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        raise crud.NotFoundError

    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)
    response = client.post(
        ROUTE_ADD_WAY_POINT_ENDPOINT.format("non-existing-route"),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 404


def test_create_waypoint_closed_route(client, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        raise crud.InvalidRequestError

    route_id = uuid.uuid4()
    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)
    response = client.post(
        ROUTE_ADD_WAY_POINT_ENDPOINT.format(route_id),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 400
