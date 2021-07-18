from fastapi import Depends, FastAPI, HTTPException
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
    except crud.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except crud.InvalidRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/route/{route_id}/length/", response_model=schemas.RouteLength)
def calculate_length(route_id: str, db: Session = Depends(get_db)):
    try:
        route_length = crud.get_route_length(db=db, route_id=route_id)
        return route_length
    except crud.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
