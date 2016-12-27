import sqlite3

db= sqlite3.connect('bollywood.db') 

c= db.cursor()
c.execute('''DROP TABLE actor''')
c.execute('''DROP TABLE movie''')

c.execute('''
	CREATE TABLE actors(
	id INTEGER PRIMARY KEY ASC, 
	name varchar(250) NOT NULL,
	resultCode INTEGER NOT NULL,
	hasTrivia BOOLEAN,
	triviaURL TEXT,
	isLegacy BOOLEAN,
	relatedToActor BOOLEAN,
	relatedToDirector BOOLEAN,
	relatedToProducer BOOLEAN,
	relatedToWriter BOOLEAN,
	isModel BOOLEAN
	)'''
)


c.execute('''
	CREATE TABLE movies (
	id INTEGER PRIMARY KEY ASC, 
	name varchar(250) NOT NULL, 
	year INTEGER, 
	genre TEXT,
	director TEXT,
	actor_id INTEGER NOT NULL, 
	FOREIGN KEY(actor_id) REFERENCES actor(id)
	)'''
)

db.commit()
db.close()