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
	#  2: IMDB result exists, but no bio
	#  3: Full bio exists, but no trivia section
	#  4: Trivia section exists, but none of my keywords found
	#  5: Trivia section exists, and one of my keywords is found

	#incoming (wiki) format: "[first name] [last name]"
	#outgoing (imdb) format: "[first name]+[last name]
	actor= actor.replace(" ","+")

	#search imdb
	imdbLink= "http://www.imdb.com/find?ref_=nv_sr_fn&q="+actor+"&s=all"
	try:
		soup= grabSiteData(imdbLink)
	except:
		return 0 #error code for 'URL choked'


	#make sure the search result is an actor Name, not a movie title or something else
	headers= soup.find_all('h3',{'class':'findSectionHeader'})
	if headers is None:
		return 1 #error code for 'no IMDB results found'

	#make sure the search result corresponds to an actor name, not a movie title or something else
	isName= -1
	for i, header in enumerate(headers):
		if header.text == "Names":
			isName= i
	if isName == -1:
		return 1.5 #there are search results, but none of them are names of actors 
	
	#grab actor name search results
	table= headers[isName].find_next_sibling('table',{"class":"findList"})


	#enter actor's page
	#RISK: get first result, hopefully it's the right one!
	urlAppend= table.find('tr').find('a')['href']
	soup= grabSiteData("http://www.imdb.com"+urlAppend)
	
	overview= soup.find("td",{"id":"overview-top"})
	if overview is None: #THIS MIGHT NOT BE NECESSARY! Keep an eye and see if 2 ever comes up. So far all 2.5
		return 2 #error code for 'IMDB result exists, but no bio'

	seeMore= overview.find("span",{"class":"see-more"})
	
	if seeMore is None:
		return 2.5 #error code for 'IMDB result exists, but no bio'
	
	bioUrlAppend= seeMore.find('a')['href']
	soup= grabSiteData("http://www.imdb.com"+bioUrlAppend)

	#enter the full bio
	groups= soup.find_all('h4',{'class':'li_group'})
	hasTrivia= -1
	for i, group in enumerate(groups):
		if "Trivia" in group.text:
			hasTrivia= i
	if hasTrivia == -1:
		return 3 #error code for Full bio exists, but no trivia section'

	#grab trivia items
	trivia= groups[hasTrivia].find_next_siblings('div',{"class":"soda"})
	return 4


if __name__=="__main__":

	print analyzeActor("Tabu")

'''
	actors= getActorsFromYear(2015)
	for actor in actors: 
		a= analyzeActor(actor)
		if a < 4:
			print actor, a
'''