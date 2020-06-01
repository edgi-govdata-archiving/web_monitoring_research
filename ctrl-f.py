#requirements
import csv
import numpy
import nltk
from nltk.corpus import stopwords
from nltk.collocations import *
#from web_monitoring.differs import _get_visible_text as gvt # import Dan Allan's page content decoder
from web_monitoring import db
from web_monitoring import internetarchive
from web_monitoring import differs
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import caffeine
import re
import fnmatch

default_stopwords = set(nltk.corpus.stopwords.words('english'))
all_stopwords = default_stopwords

keywords = {}
final_urls={}

#ancillary count functions
def count(term, visible_text): # this function counts single word terms from the decoded HTML
    term = term.lower()  # normalize so as to make result case insensitive
    tally = 0
    for section in visible_text:
    	##bigram here. instead of section.split, bigram the section
        for token in section.split():
            token = re.sub(r'[^\w\s]','',token)#remove punctuation
            tally += int(term == token.lower()) # instead of in do ==
    #print(term, tally)
    return tally

def two_count (term, visible_text): #this function counts phrases from the decoded HTML
	tally = 0
	length = len(term)
	for section in visible_text:
		tokens = nltk.word_tokenize(section)
		tokens = [x.lower() for x in tokens] #standardize to lowercase
		tokens = [re.sub(r'[^\w\s]','',x) for x in tokens]
		grams=nltk.ngrams(tokens,length)
		fdist = nltk.FreqDist(grams)
		tally += fdist[term[0].lower(), term[1].lower()] #change for specific terms
	#print(term, tally)    
	return tally

def keyword_function(visible_text):
    #based on https://www.strehle.de/tim/weblog/archives/2015/09/03/1569
    keydump=[]
    #visible_text = gvt(content)
    new_string = "".join(visible_text)
    words = nltk.word_tokenize(new_string)
    # Remove single-character tokens (mostly punctuation)
    words = [word for word in words if len(word) > 1]
    # Remove numbers
    words = [word for word in words if not word.isnumeric()]    
    # Lowercase all words (default_stopwords are lowercase too)
    words = [word.lower() for word in words]
    # Remove stopwords
    words = [word for word in words if word not in all_stopwords]
    # Calculate frequency distribution
    fdist = nltk.FreqDist(words)
    # Output top 50 words
    for word, frequency in fdist.most_common(3):
        keydump.append(word)
    #print(keydump)
    return keydump
            
def counter(file, terms, dates):
    #counts a set of one or two word terms during a single timeframe
    #dates should be in the following form: [starting year, starting month, starting day, ending year, ending month, ending day]
    #terms should be in the format ["term"], as a phrase: ["climate", "change"], or as a set of terms and/or phrases: ["climate", ["climate", "change"]]
    
    with open(file) as csvfile: 
        read = csv.reader(csvfile)
        data = list(read)
    csvfile.close()

    #terms=['adaptation', ['Agency', 'Mission'], ['air', 'quality'], 'anthropogenic', 'benefits', 'Brownfield', ['clean', 'energy'], 'Climate', ['climate', 'change'], 'Compliance', 'Cost-effective', 'Costs', 'Deregulatory', 'deregulation', 'droughts', ['economic', 'certainty'], ['economic', 'impacts'], 'economic', 'Efficiency', 'Emissions', ['endangered', 'species'], ['energy', 'independence'], 'Enforcement', ['environmental', 'justice'], ['federal', 'customer'], ['fossil', 'fuels'], 'Fracking', ['global', 'warming'], 'glyphosate', ['greenhouse', 'gases'], ['horizontal', 'drilling'], ['hydraulic', 'fracturing'], 'Impacts', 'Innovation', 'Jobs', 'Mercury', 'Methane', 'pesticides', 'pollution', 'Precautionary', ['regulatory', 'certainty'], 'regulation', 'Resilience', 'Risk', 'Safe', 'Safety', ['sensible', 'regulations'], 'state', 'storms', 'sustainability', 'Toxic', 'transparency', ['Unconventional', 'gas'], ['unconventional', 'oil'], ['Water', 'quality'], 'wildfires']
    #counter("EDGI/inputs/all Versionista URLs 10-16-18.csv", terms, [2016, 1,1,2016,7,1]) #[2018,1,1,2018,7,1]
    
    row_count = len(data)
    column_count = 2 #len(terms) 
    matrix = numpy.zeros((row_count, column_count),dtype=numpy.int16) 
    print(row_count, column_count)
    
    for pos, row in enumerate(data):
          thisPage = row[0] #change for specific CSVs
          try:
              with internetarchive.WaybackClient() as client:
                   dump = client.list_versions(thisPage, from_date=datetime(dates[0], dates[1],dates[2]), to_date=datetime(dates[3], dates[4], dates[5])) # list_versions calls the CDX API from internetarchive.py from the webmonitoring repo
                   versions = reversed(list(dump))
                   for version in versions: # for each version in all the snapshots
                       if version.status_code == '200' or version.status_code == '-': # if the IA snapshot was viable
                          url=version.raw_url
                          contents = requests.get(url).content.decode() #decode the url's HTML
                          contents = BeautifulSoup(contents, 'lxml')
                          body=contents.find('body')
                          d=[s.extract() for s in body('footer')]
                          d=[s.extract() for s in body('header')]
                          d=[s.extract() for s in body('nav')]
                          d=[s.extract() for s in body('script')]
                          d=[s.extract() for s in body('style')]
                          d=[s.extract() for s in body.select('div > #menuh')] #FWS
                          d=[s.extract() for s in body.select('div > #siteFooter')] #FWS
                          d=[s.extract() for s in body.select('div.primary-nav')] #DOE
                          d=[s.extract() for s in body.select('div > #nav-homepage-header')] #OSHA
                          d=[s.extract() for s in body.select('div > #footer-two')] #OSHA
                          del d
                          body=[text for text in body.stripped_strings]
                          for p, t in enumerate(terms):
                                if type(t) is list:
                                    page_sum = two_count(t, body)
                                else:
                                    page_sum = count(t, body)
                                matrix[pos][p]=page_sum #put the count of the term in the matrix
                          keywords[url] = keyword_function(body)
                          final_urls[thisPage]=url#[url, row[3]]
                          print(pos)
                          break
                       else:
                          pass
          except:
              print("fail")
              #print("No snapshot or can't decode", thisPage)
              final_urls[thisPage]=""
              matrix[pos]=999
         
    unique, counts = numpy.unique(matrix, return_counts=True)
    results = dict(zip(unique, counts))
    print (results)
    
    #for writing term count to a csv. you will need to convert delimited text to columns and replace the first column with the list of URLs

    with open('counts.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in matrix:
            writer.writerow(row)
    csvfile.close()

    #print out urls in separate file
    with open('urls.csv','w') as output:
        writer=csv.writer(output)
        for item in final:#final_urls.items():
            writer.writerow([item['url'], item['terms']])
    output.close()

    #print out keywords in separate file
    with open("keywords.csv", "w", encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        for key, value in keywords.items():
            try:
                writer.writerow([key, value[0], value[1], value[2]])
            except IndexError:
                writer.writerow([key, "ERROR"])
    outfile.close()

    print("The program is finished!")
    
# =============================================================================
    # correct processing errors
#  file="EDGI/outputs/dump/count_processedTZ.csv"
#  
#  with open(file)as csvfile:
#      read=csv.reader(csvfile)
#      newcounts=list(read)
#  
#  file="EDGI/outputs/main/term count trump1-7/trump_count_WMcorrected.csv"
#  
#  with open(file)as csvfile:
#      read=csv.reader(csvfile)
#      t=list(read)
# 
# 
# for r in t:
#     url=r[0]
#     if len(r[2])==0:
#         for row in newcounts:
#             if row[0]==url:
#                 r[2:59]=row[1:58]
#           
#  for rr in t:
#      if len(rr[2])==0:
#          rr[2] = "NA"    
# 
# 
#  with open('EDGI/outputs/dump/count_outputFINALTZ.csv', 'w', newline='') as csvfile:
#      writer = csv.writer(csvfile, delimiter=' ')
#      for x in t:
#          writer.writerow(x)
# =============================================================================

def matrix(): 
    #Alternative to linker that directly prepares output for Gephi network visualization 

	#2016 - End of Term
	#none = 0 
	connection = 1
	decoding_error = 8

	#S19 #Comment these otu to run 2016
	#none = 0 
	connection = 3
	decoding_error = 14

	# 0 - no connections either timeframe
	# 1 - connection in obama, removed in Trump
	# 3 - connection in trump, not in obama
	# 4 - connections in both
	# 8 - error in obama, no connection trump
	# 11 - error in obama, connection in trump
	# 14 - no connection obama, error trump
	# 15 - connection obama, error trump
	# 22 = error boths

	l=[] #master indexed list of urls (from Wayback Machine scraping)
	l_full=list(shared_final.keys()) # ???

	matrixS19 = numpy.zeros((len(l), len(l)),dtype=numpy.int8)

	#go through
	for pos,url in enumerate(l):
	    #print(url[19:])
	    #print(shared_final[url])
	    #parse url
	    thisPage = "https://www.epa.gov"+url #WMurls_linker_August2019.csv???
	    wmurl=shared_final[thisPage][1] #2016-EOT = [0], [1] = summer19
	    try:
	        contents = requests.get(wmurl).content.decode() #decode the url's HTML
	        contents = BeautifulSoup(contents, 'lxml')
	        d=[s.extract() for s in contents('script')]
	        d=[s.extract() for s in contents('style')]
	        del d
	        contents=contents.find("body")
	        links = contents.find_all('a') #find all outgoing links
	        for link in links:
	            try:
	                index = l.index(link['href'])
	                matrixS19[pos][index] = connection
	            except ValueError: #link not in our list l
	                index = -1
	            except KeyError: #no href in the link
	                pass
	        print(pos)
	    except:
	        print("decoding error")
	        matrixS19[pos] = decoding_error # code for indicating decoding error

	diffmatrix = matrix + matrixS19
	    
	#find frequently linked to and linking urls
	frequently_linkedto_S19=[] #S19 or EOT 
	col = 0
	while col < len(l_full):
	    #print(numpy.mean(matrix[:,col]))
	    if numpy.mean(matrixS19[:,col]) > 3: # matrix
	        frequently_linkedto_S19.append(l_full[col])
	    col+=1   
	    
	frequently_linking_S19=[] #S19 or EOT
	row = 0
	while row < len(l_full):
	    #print(numpy.mean(matrix[:,col]))
	    if numpy.mean(matrixS19[row,:]) > .05 and numpy.mean(matrixS19[row,:]) < 14: # matrixS19
	        frequently_linking_S19.append(l_full[row])
	    row+=1  

	#find connections existing in Obama era, but that were removed    
	results = numpy.where(diffmatrix[:,537] == 1)
	listOfCoordinates= list(zip(results[0], results[1]))
	removedConnections = []
	for coord in listOfCoordinates:
	    cs = list(coord)
	    fr = l_full[cs[0]]
	    to = l_full[cs[1]]          
	    removedConnections.append([fr, to])
	    
	#construct the network graph (for gephi)
	#form: 
	# urlA urlA self
	# urlA urlB both
	# urlA urlC removed
	# urlB urlA both
	# urlB urlB self
	# urlB urlC both
	# in this example, uralA does not link to C in 2019
	fullresults=[]
	results_lost = numpy.where(diffmatrix == 1)
	results_added = numpy.where(diffmatrix == 3)
	results_both = numpy.where(diffmatrix == 4)      
	listOfCoordinates= list(zip(results_both[0], results_both[1]))
	for coord in listOfCoordinates:
	    cs = list(coord)
	    fr = l_full[cs[0]]
	    to = l_full[cs[1]] 
	    typ = "both"         
	    fullresults.append([fr, to, typ])
	#find the pages not represented i.e. with columns 8/0 and rows 8/0 ????
	# just add all pages to end of full results?
	for url in l_full:
	    fullresults.append([url,"",""])
