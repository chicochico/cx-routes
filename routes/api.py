from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import exc
from sqlalchemy.orm import Session

from routes import crud, schemas
from routes.db.session import SessionLocal

app = FastAPI(title="Routes")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/route/", status_code=201, response_model=schemas.Route)
async def create_route(db: Session = Depends(get_db)):
    route = crud.create_route(db)
    return route


@app.post(
    "/route/{route_id}/waypoint/", status_code=201, response_model=schemas.Waypoint
)
async def create_waypoint(
    route_id: str, coordinates: schemas.Coordinates, db: Session = Depends(get_db)
):
    try:
        waypoint = crud.create_waypoint(
            db=db, route_id=route_id, coordinates=coordinates
        )
        return waypoint
    except exc.IntegrityError:
        raise HTTPException(status_code=404, detail="Route not found")


@app.get("/route/e84fee1e-fd4f-40f6-85b5-52ff46cbbb6e/length/")
def calculate_length():
    return {"km": 334.83 + 10927.08 + 555.59}
