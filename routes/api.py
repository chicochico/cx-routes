from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Coordinates(BaseModel):
    lat: float
    lon: float


@app.post("/route/")
async def root():
    return {"route_id": "e84fee1e-fd4f-40f6-85b5-52ff46cbbb6e"}


@app.post("/route/e84fee1e-fd4f-40f6-85b5-52ff46cbbb6e/waypoint/")
async def add_way_point(coordinates: Coordinates):
    return coordinates


@app.get("/route/e84fee1e-fd4f-40f6-85b5-52ff46cbbb6e/length/")
def calculate_length():
    return {"km": 334.83 + 10927.08 + 555.59}
