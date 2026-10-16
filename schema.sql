DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS departures;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS guides;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE guides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    experience_years INTEGER NOT NULL,
    languages TEXT NOT NULL,
    certificates TEXT NOT NULL,
    bio TEXT NOT NULL
);

CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    region TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    distance_km REAL NOT NULL,
    elevation_gain_m INTEGER NOT NULL,
    max_altitude_m INTEGER NOT NULL,
    duration TEXT NOT NULL,
    days INTEGER NOT NULL,
    price INTEGER NOT NULL,
    group_size INTEGER NOT NULL,
    featured INTEGER NOT NULL DEFAULT 0,
    summary TEXT NOT NULL,
    description TEXT NOT NULL,
    profile TEXT NOT NULL,
    itinerary TEXT NOT NULL,
    gear TEXT NOT NULL,
    guide_id INTEGER NOT NULL REFERENCES guides (id)
);

CREATE TABLE departures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL REFERENCES routes (id) ON DELETE CASCADE,
    starts_on TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    reserved INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    departure_id INTEGER NOT NULL REFERENCES departures (id) ON DELETE CASCADE,
    participants INTEGER NOT NULL CHECK (participants BETWEEN 1 AND 4),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departures_route ON departures (route_id, starts_on);
CREATE INDEX idx_bookings_user ON bookings (user_id);
CREATE UNIQUE INDEX idx_bookings_active ON bookings (user_id, departure_id) WHERE status = 'active';
