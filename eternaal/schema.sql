DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS venue;
DROP TABLE IF EXISTS destination;

CREATE TABLE destination (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    availability INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE venue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    price REAL NOT NULL,
    image_url TEXT,
    availability INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (destination_id) REFERENCES destination (id)
);

CREATE TABLE booking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    destination_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (destination_id) REFERENCES destination (id),
    FOREIGN KEY (venue_id) REFERENCES venue (id)
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'customer' -- 'admin' or 'customer'
);
