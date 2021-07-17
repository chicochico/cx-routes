from sqlalchemy.orm import Session

from routes import models


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


def create_waypoint(db: Session, route_id: str, coordinates: models.Waypoint):
    db_coordinates = create_db_instance(
        db=db, model=models.Waypoint, route_id=route_id, **coordinates.dict()
    )
    return db_coordinates
