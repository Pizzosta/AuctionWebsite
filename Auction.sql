-- Active: 1697120445230@@127.0.0.1@3306@Auction
drop DATABASE kawodze;

CREATE DATABASE kawodze;

USE kawodze;

/*INSERT INTO user (firstname, lastname, username, email, password)
VALUES ('Pizzosta', 'Pizzosta', 'Pizzosta', 'Pizzosta@g.mail', 'generate_password_hash(
            'Pizzosta@1', method='scrypt')');

INSERT INTO auction (title, description, created_at, start_time, end_time, starting_bid, deleted, user_id)
VALUES ('Sample Auction', 'This is a test auction', '2023-10-11 10:00:00', '2023-10-12 12:00:00', '2023-10-15 12:00:00', 100.00, 0, 1);
/* 2023-10-12 17:10:23 [288 ms] */ 
