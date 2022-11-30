
create table if not EXISTS cards (
  userid string not null,
  id integer primary key autoincrement,
  type tinyint not null, /* 1 for vocab, 2 for formulae */
  front text not null,
  back text not null,
  known boolean default 0
);

CREATE TABLE if not EXISTS users(
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    username        TEXT NOT NULL UNIQUE,
                    email           STRING NOT NULL UNIQUE,
                    description     TEXT,
                    location        STRING NOT NULL,
                    password        TEXT NOT NULL
);
