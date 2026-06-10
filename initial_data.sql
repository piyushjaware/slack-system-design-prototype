CREATE TABLE IF NOT EXISTS users
(
    id
    INT
    AUTO_INCREMENT
    PRIMARY
    KEY,
    name
    VARCHAR
(
    100
) NOT NULL,
    email VARCHAR
(
    255
) NOT NULL
    );

CREATE TABLE IF NOT EXISTS channels
(
    id
    INT
    AUTO_INCREMENT
    PRIMARY
    KEY,
    name
    VARCHAR
(
    100
) NOT NULL,
    type VARCHAR
(
    50
) NOT NULL
    );

CREATE TABLE IF NOT EXISTS msgs
(
    id
    INT
    AUTO_INCREMENT
    PRIMARY
    KEY,
    text
    TEXT
    NOT
    NULL,
    channel_id
    INT
    NOT
    NULL,
    sender_id
    INT
    NOT
    NULL,
    FOREIGN
    KEY
(
    channel_id
) REFERENCES channels
(
    id
),
    FOREIGN KEY
(
    sender_id
) REFERENCES users
(
    id
)
    );

CREATE TABLE IF NOT EXISTS channel_membership
(
    user_id
    INT
    NOT
    NULL,
    channel_id
    INT
    NOT
    NULL,
    PRIMARY
    KEY
(
    user_id,
    channel_id
),
    FOREIGN KEY
(
    user_id
) REFERENCES users
(
    id
),
    FOREIGN KEY
(
    channel_id
) REFERENCES channels
(
    id
)
    );

INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com'),
       ('Bob', 'bob@example.com'),
       ('Charlie', 'charlie@example.com');

INSERT INTO channels (name, type)
VALUES ('alice,bob', 'dm'),
       ('general', 'channel');

INSERT INTO channel_membership (user_id, channel_id)
VALUES (1, 1),
       (2, 1),
       (1, 2),
       (2, 2),
       (3, 2);

INSERT INTO msgs (text, channel_id, sender_id)
VALUES ('Hi Bob!', 1, 1),
       ('Hey Alice, nice to meet you here.', 1, 2),
       ('Welcome everyone to #general', 2, 3)
