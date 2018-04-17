drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  file_name text not null,
  output_text text not null
);