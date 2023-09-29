-- create table for rainfall.csv
-- used built in import function to import csv data to table
create table rainfall (
	index_num int not null primary key,
	station_ID varchar (5) not null,
	precipitation decimal (10,2),
	avg_precipitation decimal (10,2),
	percent_of_avg int,
	month_num int,
	year_num int,
	foreign key (station_ID) references rain_stations(station_ID)
);

-- create table for rain_stations.csv
-- used built in import function to import csv data to table
create table rain_stations(
	station_ID varchar (5) not null primary key,
	station_name varchar (200) not null,
	station_lon decimal (10,3),
	station_lat decimal (10,3),
	elevation int,
	station_link varchar
);


-- create table for forest fires csv
-- used built in import function to import csv data to table
create table fires (
	acres_burned
	fire_incident
	fire_lat
	fire_lon
	start_month
	start_year
	fire_ID
);
