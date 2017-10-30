drop table users;
create table users (
    id int primary key,
    name varchar(80),
    avatar int,
    email varchar(80),
    password varchar(80),
    dateofjoin date,
    account_balance int
);

drop table items;
create table items(
    id varchar(80),
    auction_id varchar(80),
    name varchar(80),
    description varchar(1000),
    picture1 varchar(80),
    picture2 varchar(80),
    picture3 varchar(80),
    start_price int,
    increment_price int,
    category int
);

drop table auctions;
create table auctions(
    id varchar(80),
    name varchar(80),
    admin_id varchar(80),
    start_time time,
    end_time time,
    entry_fee int
);

drop table bids;
create table bids(
    id varchar(80),
    item_id varchar(80),
    bid_amount int,
    bid_time time,
    user_id varchar(80),
    auction_id varchar(80)
);

drop table categories;
create table categories(
    id varchar(80),
    name varchar(80)
);