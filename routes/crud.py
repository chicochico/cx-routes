import datetime as dt

from sqlalchemy import exc
from sqlalchemy.orm import Session

from routes import models, schemas


class NotFoundError(Exception):
    pass


class InvalidRequestError(Exception):
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
    route = db.query(models.Route).where(models.Route.id == route_id).first()
    if route:
        try:
            db_coordinates = create_db_instance(
                db=db,
                model=models.Waypoint,
                route=route,
                coordinates=point,
            )
            return db_coordinates
        except ValueError as e:
            raise InvalidRequestError(str(e))
    else:
        raise NotFoundError(f"Route with id: {route_id} not found")


def get_route_length(db: Session, route_id: str):
    route = db.query(models.Route).where(models.Route.id == route_id).first()

    if route:
        return schemas.RouteLength(
            route_id=route.id, km=route.calculate_length_in_km(db)
        )
    else:
        raise NotFoundError(f"Route with id: {route_id} not found")


def get_longest_route_for_day(db: Session, date: dt.date):
    if date >= dt.datetime.utcnow().date():
        raise InvalidRequestError("Can only get longest route for past dates")
    else:
        try:
            return models.Route.get_longest_route_for_day(db=db, date=date)
        except exc.NoResultFound:
            raise NotFoundError("No route found")
