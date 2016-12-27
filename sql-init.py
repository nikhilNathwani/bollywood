import sqlite3

db= sqlite3.connect('bollywood.db') 

c= db.cursor()

c.execute('''
	CREATE TABLE actor(
	id INTEGER PRIMARY KEY ASC, 
	name varchar(250) NOT NULL,
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
	CREATE TABLE movie (
	id INTEGER PRIMARY KEY ASC, 
	name varchar(250) NOT NULL, 
	year INTEGER, 
	actor_id INTEGER NOT NULL, 
	FOREIGN KEY(actor_id) REFERENCES actor(id)
	)'''
)

db.commit()
db.close()