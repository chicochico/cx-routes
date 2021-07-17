from sqlalchemy import exc
from sqlalchemy.orm import Session

from routes import models, schemas


class NotFoundError(Exception):
    pass


def create_db_instance(db: Session, model, **kwargs):
    """
    Create an entry of the model in the database
    """
    instance = model(**kwargs)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def create_route(db: Session):
    db_route = create_db_instance(db=db, model=models.Route)
    return db_route


def create_waypoint(db: Session, route_id: str, coordinates: schemas.Waypoint):
    point = f"POINT({coordinates.lat} {coordinates.lon})"
    try:
        db_coordinates = create_db_instance(
            db=db, model=models.Waypoint, route_id=route_id, coordinates=point
        )
        return db_coordinates
    except exc.IntegrityError:
        raise NotFoundError(f"Route with id: {route_id} not found")


def get_route_length(db: Session, route_id: str):
    route = db.query(models.Route).where(models.Route.id == route_id).first()

    if route:
        return schemas.RouteLength(
            route_id=route.id, km=route.calculate_length_in_km(db)
        )
    else:
        raise NotFoundError(f"Route with id: {route_id} not found")
