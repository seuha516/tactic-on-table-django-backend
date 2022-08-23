-- os.environ 오류.. 수동으로 대체할 것

CREATE SCHEMA `tactic_on_table_db` DEFAULT CHARACTER SET utf8mb4;
use tactic_on_table_db;

create user 'tactic_on_table_user'@'localhost' identified by 'qdted7Z6Q!';
grant all privileges on tactic_on_table_db.* to 'tactic_on_table_user'@'localhost';
FLUSH PRIVILEGES;

CREATE TABLE `account` (
  `username` VARCHAR(16) NOT NULL PRIMARY KEY,
  `hashed_password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `nickname` VARCHAR(12) NOT NULL UNIQUE,
  `image` VARCHAR(255) NOT NULL,
  `total_score` INT NOT NULL,
  `score` JSON NOT NULL
  );

CREATE TABLE `match_record` (
  `num` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `game` INT NOT NULL,
  `players` JSON NOT NULL,
  `result` JSON NOT NULL,
  `date` datetime NOT NULL
);

CREATE TABLE `room` (
  `num` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `code` VARCHAR(16) NOT NULL,
  `name` VARCHAR(30) NOT NULL,
  `password` VARCHAR(60) NOT NULL,
  `color` VARCHAR(10) NOT NULL,
  `game` INT NOT NULL,
  `max_player` INT NOT NULL,
  `players` JSON NOT NULL,
  `status` INT NOT NULL,
  `data` JSON
);

INSERT INTO account VALUES('user1', 'xxxxxxxx', 'user@naver.com', 'User유저1','test1.png', 126, '[10, 20, 70, 800, 0, 0, 0, 0, 0, 0, 0, 0]');
INSERT INTO account VALUES('user2', 'xxxxxxxx', 'user@naver.com', 'User유저2','test2.png', 126, '[103,21,1,1,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user3', 'xxxxxxxx', 'user@naver.com', 'User유저3','test3.png', 0, '[0,0,0,0,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user4', 'xxxxxxxx', 'user@naver.com', 'User유저4','test4.png', 8, '[1,2,3,2,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user5', 'xxxxxxxx', 'user@naver.com', 'User유저5','test5.png', 13, '[4,2,3,4,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user6', 'xxxxxxxx', 'user@naver.com', 'User유저6','test6.png', 99, '[10,25,32,32,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user7', 'xxxxxxxx', 'user@naver.com', 'User유저7','test7.png', 321, '[13,8,193,107,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user8', 'xxxxxxxx', 'user@naver.com', 'User유저8','test8.png', 263, '[1,211,43,8,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user9', 'xxxxxxxx', 'user@naver.com', 'User유저9','test9.png', 1260, '[1023,200,30,7,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user10', 'xxxxxxxx', 'user@naver.com', 'User유저10','test10.png', 900, '[10,20,70,800,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user11', 'xxxxxxxx', 'user@naver.com', 'User유저11','test11.png', 81, '[7,6,3,65,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user12', 'xxxxxxxx', 'user@naver.com', 'User유저12','test12.png', 3, '[0,0,0,3,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user13', 'xxxxxxxx', 'user@naver.com', 'User유저13','test13.png', 8, '[1,2,1,4,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user14', 'xxxxxxxx', 'user@naver.com', 'User유저14','test14.png', 17, '[2,2,8,5,0,0,0,0,0,0,0,0]');
INSERT INTO account VALUES('user15', 'xxxxxxxx', 'user@naver.com', 'User유저15','test15.png', 112, '[12,9,11,80,0,0,0,0,0,0,0,0]');

INSERT INTO match_record VALUES(NULL, 0, '["user1","user2"]', '{"type":"1on1","winner":"user1"}', "1998-12-31 23:59:59");
INSERT INTO match_record VALUES(NULL, 1, '["user3","user4","user5","user6","user7","user8"]', '{"type":"multi","winner":"user4"}', "2021-12-31 23:59:59");
INSERT INTO match_record VALUES(NULL, 2, '["user1","user3"]', '{"type":"1on1","winner":"user3"}', "2021-12-31 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user2","user4"]', '{"type":"1on1","winner":"user4"}', "2021-09-30 23:59:59");
INSERT INTO match_record VALUES(NULL, 0, '["user5","user1"]', '{"type":"1on1","winner":"user1"}', "2021-11-22 23:59:59");
INSERT INTO match_record VALUES(NULL, 1, '["user8","user4"]', '{"type":"multi","winner":"user4"}', "2022-05-19 23:59:59");
INSERT INTO match_record VALUES(NULL, 2, '["user4","user7"]', '{"type":"1on1","winner":"user7"}', "2022-06-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user3","user2"]', '{"type":"1on1","winner":"user3"}', "2022-05-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 0, '["user5","user2"]', '{"type":"1on1","winner":null}', "2022-04-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 1, '["user1","user4","user5"]', '{"type":"multi","winner":"user4"}', "2022-03-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 2, '["user3","user6"]', '{"type":"canceled"}', "2022-01-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user11","user6"]', '{"type":"canceled"}', "2022-08-06 23:59:59");
INSERT INTO match_record VALUES(NULL, 0, '["user12","user13"]', '{"type":"canceled"}', "2022-05-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 1, '["user3","user2","user14","user1"]', '{"type":"canceled"}', "2022-08-06 21:59:59");
INSERT INTO match_record VALUES(NULL, 2, '["user7","user2"]', '{"type":"1on1","winner":"user7"}', "2022-07-27 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user7","user3"]', '{"type":"1on1","winner":"user3"}', "2022-07-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 2, '["user722","user2"]', '{"type":"1on1","winner":"user722"}', "2022-07-27 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user147","user314"]', '{"type":"1on1","winner":"user314"}', "2022-07-07 23:59:59");
INSERT INTO match_record VALUES(NULL, 3, '["user1","user314"]', '{"type":"1on1","winner":"user314"}', "2022-07-07 23:59:59");
