from util import *


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

	#only looks at actors within an <a> tag for now
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
	#  2: IMDB result exists, but no bio
	#  3: Full bio exists, but no trivia section
	#  4: Trivia section exists, but none of my keywords found
	#  5: Trivia section exists, and one of my keywords is found

	#incoming (wiki) format: "[first name] [last name]"
	#outgoing (imdb) format: "[first name]+[last name]
	actor= actor.replace(" ","+")
	print actor

	#search imdb
	imdbLink= "http://www.imdb.com/find?ref_=nv_sr_fn&q="+actor+"&s=all"
	try:
		soup= grabSiteData("poo")
	except:
		return 0 #error code for Ur


if __name__=="__main__":
	a= getActorsFromYear(2015)
	print a[7]