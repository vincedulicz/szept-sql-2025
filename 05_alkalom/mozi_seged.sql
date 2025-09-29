
--  ####  START tábla létrehozássa ####  --

create table if not exists mozik(
	id serial primary key,
	nev varchar(100) not null,
	varos varchar(100) not null
);


create table if not exists dolgozok(
	id serial primary key,
	nev varchar(100) not null,
	beosztas varchar(100),
	mozi_id int references mozik(id) -- külső kulcs
);


create table if not exists bufek(
	id serial primary key,
	nev varchar(100) not null,
	mozi_id int references mozik(id)
);


create table if not exists vasarlok(
	id serial primary key,
	nev varchar(100) not  null,
	vip boolean default false
);


create table if not exists filmek(
	id serial primary key,
	cim varchar(200) not null,
	kategoria varchar(50),
	besorolas varchar(25)
);



--  ####  END tábla létrehozássa ####  --


-- ### xxx ###


--  ####  START Dummy adatok beszúrása ####  --


insert into mozik (nev, varos) values
('Cinema City', 'Budapest'),
('Pláza Mozi', 'Debrecen'),
('Belvárosi Mozi', 'Szeged'),
('FilmPalota', 'Pécs');


insert into dolgozok (nev, beosztas, mozi_id) values
('Kovács Péter', 'Pénztáros', 1),
('Nagy Anna', 'Ügyfélszolgálat', 2),
('Tóth Gábor', 'Vetítőgép-kezelő', 3),
('Szabó Katalin2', 'Büfévezető', 4)

insert into dolgozok (nev, beosztas, mozi_id) values
('Kovács Péter', 'Pénztáros', 2),
('Nagy Anna2', 'Ügyfélszolgálat', 2),
('Tóth Gábor2', 'Vetítőgép-kezelő', 3),
('Szabó Katalin2', 'Büfévezető', 3);


insert into bufek (nev, mozi_id) values
('Popcoin King', 1),
('Snack Bar', 2),
('Cinema Snacks', 3),
('Movie Bites', 4);




insert into vasarlok (nev, vip) values
('Horváth István', TRUE),
('Farkas Éva', FALSE),
('Varga Zoltán', TRUE),
('Kiss Júlia', FALSE);





insert into filmek (cim, kategoria, besorolas) values
('Eredet', 'Sci-Fi', '16+'),
('Titanic', 'Dráma', '12+'),
('Star Wars', 'Sci-Fi', '12+'),
('Joker', 'Thriller', '18+'),
('Eredet2', 'Sci-Fi', '16+');




--  ####  END Dummy adatok beszúrása ####  --




--  #### START lekérdezések ####  --


select * from filmek;