# Routes

## Exercise
Create an application that accepts data from a GPS tracker device. It starts by requesting the creation of a route, afterwards it streams WGS84 coordinates to the endpoint. The route is expected to de finished within one day, at which point no more coordinates will be accepted.
At some point the length of the route can be queried.

Include an endpoint to query for the longest path of past days. Routes created in the past cannot be modified.

## Requirements
REST api to store GPS coordinates:

- create route (sequence of WGS84 coordinates)
- add coordinates to existing route
- routes must be done within a day (24h from time of creation or midnigt?)
    - after end no more coordinates are accepted for this route
    - route lenght is calculated
- longest route for a day should be calculated

## Assumptions
- empty POST request creates a new route (returning the route id)
- route id is a UUID
- "A route is expected to be done within a day"
    - will be taken as a route can start at any time but must end at most in the same day at 23:59
- longest route for each day is the route with the longest lenght from all the routes of the same day
- authentication is not required
- api endpoints interface should be kept the same
- times are stored in utc

## Implementation
FastAPI was used for the API server, and for data storage PostGis. SqlAlchemy + GeoAlchemy2 were used to interface with the database, to store routes data, and use the spatial functions provided by PostGis.

## Running
NOTE: In production replace the database variables in `docker-compose.yaml` with the production database values.

To execute the app run:
```
docker compose up --build
```
An API endpoint will be avaliable at `http://localhost:8000/`. And documention about the endpoints can be found at [http://localhost:8000/docs#/](http://localhost:8000/docs#/).

### Running tests
Build the image
```
docker build -t routes_webserver .
```

To run unit tests:
```
docker run --rm --entrypoint pytest routes_webserver tests/test*
```

To run integration tests:
```
docker compose up -d

# then run the test command
docker exec routes_webserver_1 pytest tests/integration* \

# and finally stop the containers
docker compose down
```

Note: Integration test for longest route depends on the state of the DB, althougt unlikely a longer route than the one used in the test can exist.


## Developing
When making changes to models new migrations can be generated with:
```
alembic revision --autogenerate -m "migration message"
```

then new migrations can be applied to the db with:
```
alembic upgrade head
```

## Future improvements
- ~get more data to implement integration tests for longest route~
- implement crud functions as async
- add authentication
