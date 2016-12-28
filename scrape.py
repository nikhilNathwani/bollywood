from util import *
import sqlite3

relations= ["great-great-grandson of","great-grandson of","granddson of","son of","great-great-granddaughter of","great-granddaughter of","granddaughter of","daughter of","sister of","brother of","nephew of","niece of"]
industryTitles= ["actress","actor","director","producer","writer"]


def buildTables(year):
	#movie list that'll eventually be thrown into tables via sqlite
	movieData= []
	#no actorData list because actor table will be constructed on the fly in the for loops 

	#get rows for movies from year X
	movies= getMoviesFromYear(year)
	numMovies= len(movies)

	for i,movie in enumerate(movies):
		print "Movie",i,"of",numMovies,"Movies"

		#analyze actors for this movie
		actors= movie['cast']

		# if cast is empty, skip over this movie, else analyze its actors
		if actors!=[]:
			for actor in actors:
				actorID= addActorData(actor)
				print actorID, actor, "\n\n"
				movieData.append([movie['title'],year,movie['genre'],movie['director'],actorID])

	addMovieData(movies)

	print "Actor and Movie data added to tables."


#returns list of {title, genre, director, cast} dicts
#for now, assumes the year is 2014 or 2015. 
def getMoviesFromYear(year):
	#year can only be in certain range
	if year not in [2014,2015]:
		raise ValueError("Year must be in [2014,2015]") 

	wikiURL= 'https://en.wikipedia.org/wiki/List_of_Bollywood_films_of_'+str(year)
	soup= grabSiteData(wikiURL)

	#there's 4 tables, one for each quarter-year
	#consolidating all rows into one list
	tables= soup.find_all('table',class_='sortable')
	rows= []
	for table in tables:
		rows += table.find_all('tr')[1:] #skip 1st row bc it's the table header

	movies= []
	for row in rows:
		movie= {}
		data= row.find_all('td')

		#movie title
		link= data[1].find('a')
		movie['title']= data[1].text if link == None else link.text
		movie['title']= movie['title'].encode('ascii', 'ignore')

		#genre
		link= data[2].find('a')
		movie['genre']= data[2].text if link == None else link.text
		movie['genre']= movie['genre'].encode('ascii', 'ignore')

		#director
		link= data[2].find('a')
		movie['director']= data[3].text if link == None else link.text
		movie['director']= movie['director'].encode('ascii', 'ignore')

		#cast
		#RISK: only looks at actors within an <a> tag for now
		cast= data[4]
		actors= cast.find_all('a')
		if actors == None:
			movie['cast']= [] 
		else:
			movie['cast']= [actorLink.text.encode('ascii', 'ignore') for actorLink in actors]

		movies.append(movie)

	return movies


#adds an actor to the actors table, and returns ID of actor
#if actor already exists in table, doesn't re-add, just returns its ID
def addActorData(actor):
	db = sqlite3.connect('bollywood.db')
	cursor= db.cursor()
	#RISK: name collisions will cause issues
	cursor.execute('''SELECT id FROM actors WHERE name=?''', (actor,))
	actor1= cursor.fetchone()

	if actor1 != None:
		return actor1[0]
	else:
		resultCode,triviaUrl,trivData= analyzeActor(actor)
		hasTrivia= (triviaUrl!="")
		isLegacy= isLineage(trivData)[0]

		db = sqlite3.connect('bollywood.db')
		cursor= db.cursor()
		cursor.execute('''INSERT INTO actors(name, resultCode, hasTrivia, triviaUrL, isLegacy, relatedToActor, relatedToDirector, relatedToProducer, relatedToWriter, isModel)
	                  VALUES(?,?,?,?,?,?,?,?,?,?)''', (actor,resultCode,hasTrivia,triviaUrl,isLegacy,None,None,None,None,None))
		db.commit()
		return cursor.lastrowid

#takes list of movie data and inserts it into movies table
#has no return value
def addMovieData(movies):
	pass


#return list of bollywood movies released in 2015
def getActorsFromYear(year):
	
	#year can only be in certain range
	if year<1920 or year>2016:
		raise ValueError("Year must be in [1920,2016]") 

	wikiURL= 'https://en.wikipedia.org/wiki/List_of_Bollywood_films_of_'+str(year)
	soup= grabSiteData(wikiURL)

	#there's 4 tables, one for each quarter-year
	#consolidating all rows into one list
	tables= soup.find_all('table',class_='sortable')
	rows= []
	for table in tables:
		rows += table.find_all('tr')[1:] #skip 1st row bc it's the table header

	actorLists= [row.find_all('td')[-2] for row in rows]

	numMovies= len(actorLists)

	#RISK: only looks at actors within an <a> tag for now
	actors= set()
	for lst in actorLists:
		lst= [elem.text.encode('ascii', 'ignore') for elem in lst.find_all('a')]
		actors.update(lst)
	actors= list(actors)

	numActors= len(actors)

	print "Num Movies:", numMovies, "Num Actors:", numActors
	return actors


def analyzeActor(actor):
	#possible categorizations
	#  0: URL choked
	#  1: no IMDB results found
	#  2: there are search results, but none of them are names of actors 
	#  3: IMDB result exists, but no bio
	#  4: IMDB result and overview exists, but no See More for full page bio
	#  5: Full bio exists, but no trivia section
	#  6: Trivia section exists, but none of my keywords found
	#  7: Trivia section exists, and one of my keywords is found

	#incoming (wiki) format: "[first name] [last name]"
	#outgoing (imdb) format: "[first name]+[last name]
	actor= actor.replace(" ","+")

	#search imdb
	imdbLink= "http://www.imdb.com/find?ref_=nv_sr_fn&q="+actor+"&s=all"
	try:
		soup= grabSiteData(imdbLink)
	except:
		return (0,"",[]) #error code for 'URL choked'


	#make sure the search result is an actor Name, not a movie title or something else
	headers= soup.find_all('h3',{'class':'findSectionHeader'})
	if headers is None:
		return (1,"",[]) #error code for 'no IMDB results found'

	#make sure the search result corresponds to an actor name, not a movie title or something else
	isName= -1
	for i, header in enumerate(headers):
		if header.text == "Names":
			isName= i
	if isName == -1:
		return (2,"",[]) #there are search results, but none of them are names of actors 
	
	#grab actor name search results
	table= headers[isName].find_next_sibling('table',{"class":"findList"})


	#enter actor's page
	#RISK: get first result, hopefully it's the right one!
	urlAppend= table.find('tr').find('a')['href']
	soup= grabSiteData("http://www.imdb.com"+urlAppend)
	
	overview= soup.find("td",{"id":"overview-top"})
	if overview is None: #THIS MIGHT NOT BE NECESSARY! Keep an eye and see if 2 ever comes up. So far all 2.5
		return (3,"",[]) #error code for 'IMDB result exists, but no bio'

	seeMore= overview.find("span",{"class":"see-more"})
	
	if seeMore is None:
		return (4,"",[]) #error code for 'IMDB result and overview exists, but no see more'
	
	try:
		bioUrlAppend= seeMore.find('a')['href']
		soup= grabSiteData("http://www.imdb.com"+bioUrlAppend)
	except httplib.BadStatusLine:
		print actor, bioUrlAppend

	#enter the full bio
	groups= soup.find_all('h4',{'class':'li_group'})
	hasTrivia= -1
	for i, group in enumerate(groups):
		if "Trivia" in group.text:
			hasTrivia= i
	if hasTrivia == -1:
		return (5,"",[]) #error code for Full bio exists, but no trivia section'

	#grab trivia items
	trivia= groups[hasTrivia].find_next_siblings('div',{"class":"soda"})

	return (6,"http://www.imdb.com"+bioUrlAppend,trivia)


#returns boolean of whether the actor has familial connections to the industry
def isLineage(trivia):	
	for item in trivia:
		for relation in relations:
			if relation in item.text.lower():
				link= item.find('a')
				if link is not None:
					relative= {'relation':relation, "name":link.text}
					print relative
					i= isInIndustry(link['href'])
					if i[0]:
						relative["job"]= i[1]
						return (True, relative)
	return (False, {})

def isInIndustry(bioUrl):
	soup= grabSiteData("http://www.imdb.com"+bioUrl)
	jobs= soup.find("div",{"class":"infobar","id":"name-job-categories"})
	if jobs==None:
		return (False, "")
	jobTitles= jobs.find_all("span")
	for title in jobTitles:
		for t in industryTitles: 
			if t in title.text.lower():
				return (True, t)
	return (False, "")
				

if __name__=="__main__":
#	a= analyzeActor("Priyanka Chopra")
#	print isLineage(a[1])

#	actors= getActorsFromYear(2015)
#	for actor in actors: 
#		a= analyzeActor(actor)
#		if a[0] == 4:
#			print actor
#			print isLineage(a[1])
#			print "\n\n"

	
#	movies= getMoviesFromYear(2014)
#	for m in movies:
#		print '\n\n'
#		print m

	buildTables(2014)

#	db = sqlite3.connect('bollywood.db')
#	cursor= db.cursor()
	#RISK: name collisions will cause issues
	#cursor.execute('''INSERT INTO actors(name, resultCode, hasTrivia, triviaUrL, isLegacy, relatedToActor, relatedToDirector, relatedToProducer, relatedToWriter, isModel)
	#                  VALUES(?,?,?,?,?,?,?,?,?,?)''', ("Bum",0,True,"",True,True,False,0,0,0))
	#db.commit()
#	cursor.execute('''SELECT id FROM actors WHERE name=?''', ("Bum",))
#	user1= cursor.fetchone()
#	print user1[0]



