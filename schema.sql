create table if not exists user (
  user_id integer primary key autoincrement,
  username text not null,
  email text not null,
  pw_hash text not null,
  signature text not null,
  reg_date not null
);

create table if not exists follower (
  who_id integer,
  whom_id integer
);

create table if not exists message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);
