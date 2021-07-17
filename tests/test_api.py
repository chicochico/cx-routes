import json
import uuid

import ipdb
import pytest
from fastapi.testclient import TestClient
from routes import crud, models, schemas
from routes.api import app
from sqlalchemy import exc

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
    expected = {"id": str(route.id), "waypoints": []}

    def mock_create_route(*args, **kwargs):
        "mock db call"
        return route

    monkeypatch.setattr(crud, "create_route", mock_create_route)

    response = client.post(ROUTE_ENDPOINT)
    assert response.status_code == 201
    assert response.json() == expected


def test_create_waypoint(client, route, monkeypatch):
    route_id = str(route.id)
    coordinates = {"lat": -25.4025905, "lon": -49.3124416}
    waypoint = models.Waypoint(route_id=route_id, **coordinates)

    expected = {
        "route_id": route_id,
        "lat": waypoint.lat,
        "lon": waypoint.lon,
    }

    def mock_create_waypoint(*args, **kwargs):
        "mock db call"
        return waypoint

    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)

    response = client.post(
        ROUTE_ADD_WAY_POINT_ENDPOINT.format(route_id), json=coordinates
    )
    assert response.status_code == 201
    assert response.json() == expected


def test_create_waypoint_invalid_route(client, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        raise exc.IntegrityError("statement", "params", "orig")

    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)

    response = client.post(
        ROUTE_ADD_WAY_POINT_ENDPOINT.format("non-existing-route"),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 404
