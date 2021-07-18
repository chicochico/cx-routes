import datetime as dt

import pytest
import requests
from fastapi.testclient import TestClient
from routes import crud, models
from routes.api import app

from tests import endpoints

client = TestClient(app)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            [
                {"lat": 52.50763, "lon": 13.35113},
                {"lat": 52.50102, "lon": 13.34626},
                {"lat": 52.49069, "lon": 13.33685},
                {"lat": 52.47946, "lon": 13.33276},
                {"lat": 52.4735, "lon": 13.32574},
            ],
            4.73264370978033,
        ),
        (
            [
                {"lat": 52.54905, "lon": 13.38535},
                {"lat": 52.58706, "lon": 13.28629},
                {"lat": 52.66963, "lon": 13.19951},
                {"lat": 52.80311, "lon": 13.04078},
                {"lat": 52.92672, "lon": 12.82153},
            ],
            75.3058862294347,
        ),
        (
            [
                {"lat": 52.54905, "lon": 13.38535},
                {"lat": 52.72948, "lon": 12.62421},
                {"lat": 53.29014, "lon": 11.54653},
                {"lat": 53.43887, "lon": 10.36742},
                {"lat": 53.53217, "lon": 10.02668},
            ],
            390.86982321966605,
        ),
        (
            [
                {"lat": 90, "lon": 180},
                {"lat": -90, "lon": -180},
            ],
            20003.931458625397,
        ),
    ],
)
def test_route_length(test_input, expected):
    response = requests.post(endpoints.ROUTE_ENDPOINT)
    route = response.json()

    for coordinates in test_input:
        client.post(
            endpoints.ROUTE_ADD_WAY_POINT_ENDPOINT.format(route["id"]), json=coordinates
        )

    length_response = client.get(
        endpoints.ROUTE_LENGTH_ENDPOINT.format(route["id"])
    ).json()

    assert length_response["km"] == pytest.approx(expected)


def test_longest_route(monkeypatch):
    """
    this test depends on DB state, altought unlikely
    is still possible for a longer route to exist in this day
    """

    def mock_get_longest_route_for_day(db, date):
        """
        bypass validation so this function can be called today
        """
        return models.Route.get_longest_route_for_day(db=db, date=date)

    monkeypatch.setattr(
        crud, "get_longest_route_for_day", mock_get_longest_route_for_day
    )

    response = client.get(
        endpoints.ROUTE_LONGEST,
        params={"date": dt.datetime.utcnow().date().isoformat()},
    ).json()

    assert response["length_km"] == pytest.approx(20003.931458625397)
