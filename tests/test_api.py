import datetime as dt
import uuid

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from routes import crud, models, schemas
from routes.api import app
from shapely.geometry import Point

from tests import endpoints


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
    expected = {"id": str(route.id), "waypoints": [], "length_km": None}
    response = client.post(endpoints.ROUTE_ENDPOINT)
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
        endpoints.ROUTE_ADD_WAY_POINT_ENDPOINT.format(route_id),
        json={"lat": lat, "lon": lon},
    )
    assert response.status_code == 201
    assert response.json() == expected


def test_create_waypoint_invalid_route(client, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        raise crud.NotFoundError

    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)
    response = client.post(
        endpoints.ROUTE_ADD_WAY_POINT_ENDPOINT.format(uuid.uuid4()),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 404


def test_create_waypoint_invalid_uuid(client):
    response = client.post(
        endpoints.ROUTE_ADD_WAY_POINT_ENDPOINT.format("invalid-id"),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 422


def test_create_waypoint_closed_route(client, monkeypatch):
    def mock_create_waypoint(*args, **kwargs):
        raise crud.InvalidRequestError

    route_id = uuid.uuid4()
    monkeypatch.setattr(crud, "create_waypoint", mock_create_waypoint)
    response = client.post(
        endpoints.ROUTE_ADD_WAY_POINT_ENDPOINT.format(route_id),
        json={"lat": -25.4025905, "lon": -49.3124416},
    )
    assert response.status_code == 400


def test_get_longest_route(client, monkeypatch):
    route_id = uuid.uuid4()
    expected = {"id": str(route_id), "waypoints": [], "length_km": None}

    def mock_get_longest_route_for_day(*args, **kwargs):
        return models.Route(id=route_id, created_at=dt.datetime.utcnow())

    monkeypatch.setattr(
        crud, "get_longest_route_for_day", mock_get_longest_route_for_day
    )

    response = client.get(
        endpoints.ROUTE_LONGEST,
        params={"date": "2021-07-17"},
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_get_longest_route_no_result(client, monkeypatch):
    def mock_get_longest_route_for_day(*args, **kwargs):
        raise crud.NotFoundError

    monkeypatch.setattr(
        crud, "get_longest_route_for_day", mock_get_longest_route_for_day
    )

    response = client.get(
        endpoints.ROUTE_LONGEST,
        params={"date": "2021-07-17"},
    )
    assert response.status_code == 404


def test_get_longest_route_invalid_date(client, monkeypatch):
    def mock_get_longest_route_for_day(*args, **kwargs):
        raise crud.InvalidRequestError

    monkeypatch.setattr(
        crud, "get_longest_route_for_day", mock_get_longest_route_for_day
    )

    response = client.get(
        endpoints.ROUTE_LONGEST,
        params={"date": "2021-07-17"},
    )
    assert response.status_code == 400


def test_route_length(client, monkeypatch):
    route_id = uuid.uuid4()
    length = 1234.0

    def mock_get_route_length(*arks, **kwargs):
        return schemas.RouteLength(route_id=route_id, km=length)

    expected = {"route_id": str(route_id), "km": length}
    monkeypatch.setattr(crud, "get_route_length", mock_get_route_length)
    response = client.get(endpoints.ROUTE_LENGTH_ENDPOINT.format(route_id))
    assert response.status_code == 200
    assert response.json() == expected


def test_route_length_not_found(client, monkeypatch):
    route_id = uuid.uuid4()

    def mock_get_route_length(*arks, **kwargs):
        raise crud.NotFoundError

    monkeypatch.setattr(crud, "get_route_length", mock_get_route_length)
    response = client.get(endpoints.ROUTE_LENGTH_ENDPOINT.format(route_id))
    assert response.status_code == 404


def test_route_length_invalid_id(client, monkeypatch):
    response = client.get(endpoints.ROUTE_LENGTH_ENDPOINT.format("not-valid-id"))
    assert response.status_code == 422
