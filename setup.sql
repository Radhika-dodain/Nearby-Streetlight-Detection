CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE street_lights(
  id SERIAL PRIMARY KEY,
  name TEXT,
  location GEOMETRY(Point, 4326)
);