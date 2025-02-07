-- -- SQLite
-- DROP TABLE IF EXISTS notifications
-- ;

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title,
    message TEXT,
);

INSERT INTO notifications (title, message) VALUES ('Welcome', 'Your registration is successful.');