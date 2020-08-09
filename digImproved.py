#!/usr/bin/python3

import httplib2
import urllib
import re
from past.builtins import execfile
from html.parser import HTMLParser

### Ustawienia
# klasa li w której są dane każdego poszczególnego znaleziska
entryClass = "^link iC( )?( hot)?$"
# klasa div z tagami
tagClass = "fix-tagline"
# modyfikator znaleziska "gorącego"
hotModifier = "hot"

# wartości do konfiguracji przez użytkownika (w osobnym pliku)
execfile('dig_settings.py')

### Początek kodu
class Entry:
	def __init__(self):
		self.eid = ""
		self.upvotes = ""
		self.intUrl = ""
		self.extUrl = ""
		self.imgPrevUrl = ""
		self.imgPrevAlt = ""
		self.lead = ""
		self.author = ""
		self.extSite = ""
		self.text = ""
		self.comments = ""
		self.dateSimple = ""
		self.dateExtend = ""
		self.dateMinsAgo = ""
		self.tags = []
		self.hotOrNot = ""

	def __str__(self):
		# jeśli wpis nie ma autora, pomijamy go
		if self.author == "":
			return ""

		# jeśli lead / text / site zewnętrzny / author / tag pasuje do filtrów, pomijamy go
		if re.match(re.compile(blacklisted_leads, flags=re.IGNORECASE), self.lead) != None:
                        return ""
		if re.match(re.compile(blacklisted_text, flags=re.IGNORECASE), self.text) != None:
                        return ""
		if re.match(re.compile(blacklisted_sites, flags=re.IGNORECASE), self.extSite) != None:
                        return ""
		if re.match(re.compile(blacklisted_authors, flags=re.IGNORECASE), self.author) != None:
                        return ""
		for tag in self.tags:
			if re.match(re.compile(blacklisted_tags, flags=re.IGNORECASE), tag) != None:
				return ""

		# pozostałe wpisy ubieramy w odpowiedni HTML i zwracamy
		HTMLOutput  = '<li class="link iC ' + self.hotOrNot + '">\n\t<div class="article  clearfix preview   dC" data-type="link" data-id="' + self.eid + '">\n\t\t'

		# czy wpis jest "gorący"?
		if self.hotOrNot == hotModifier:
			HTMLOutput += '<i class="icon hot"></i>\n\t\t'

		HTMLOutput += '<div class="diggbox ">\n\t\t\t<a href="#' + self.eid + '" data-ajaxurl="" title="wykop to znalezisko" class="ajax">\n\t\t\t\t<span>' + self.upvotes
		HTMLOutput += '</span>\n\t\t\t</a>\n\t\t</div>\n\n\n\n\n\t\t<div class="media-content m-reset-float ">\n\t\t\t<a href="' + self.intUrl + '" rel="nofollow noopener noreferrer" title="" >\n\t\t\t\t<img src="'
		HTMLOutput += self.imgPrevUrl + '"  alt="' + self.imgPrevAlt + '">\n\t\t\t</a>\n\t\t</div>\n\n\t\t<div class="lcontrast m-reset-margin">\n\t\t\t<h2>\n\t\t\t\t<a href="' + self.intUrl
		HTMLOutput += '" rel="nofollow noopener noreferrer" title="' + self.lead + '" >' + self.imgPrevAlt + '</a>\n\t\t\t</h2>\n\n\t\t\t<div class="fix-tagline">\n\t\t\t\t<a class="color-2 affect" href="https://www.wykop.pl/ludzie/'
		HTMLOutput += self.author + '/"><em>@</em>' + self.author + '</a>\n\n\t\t\t\t<span class="tag create">\n\t\t\t\t\t<a class="affect" href="' + self.extUrl
		HTMLOutput += '" title="Otwórz źródło znaleziska" rel="nofollow noopener" target="_blank">' + self.extSite + '</a>\n\t\t\t\t</span>\n\n\t\t\t\t<span class="tag create">\n\t\t\t\t\t<a class="affect"  href="https://www.wykop.pl/domena/'
		HTMLOutput += self.extSite + '/" title="Zobacz inne znaleziska z tej domeny" />\n\t\t\t\t</span>\n\n'

		# tagi dodajemy w specjalny sposób
		for Tag in self.tags:
			HTMLOutput += '\t\t\t\t<a class="tag affect create " href="https://www.wykop.pl/tag/' + Tag + '/"><em>#</em>' + Tag + '</a>\n'

		HTMLOutput += '\t\t\t</div>\n\n\t\t\t<div class="description">\n\t\t\t\t<p class="text">\n\t\t\t\t\t<a href="' + self.intUrl + '" title="">\n\t\t\t\t\t' + self.text
		HTMLOutput += '\n\t\t\t\t\t</a>\n\t\t\t\t</p>\n\t\t\t</div>\n\n\t\t\t<div class="row elements">\n\t\t\t\t<a class="affect" href="' + self.intUrl + '">' + self.comments
		HTMLOutput += '</a>\n\n\t\t\t\t<span class="affect">opublikowany \n\t\t\t\t\t<time title="' + self.dateSimple + '" datetime="' + self.dateExtend + '" itemprop="datePublished">'
		HTMLOutput += self.dateMinsAgo + '</time>\n\t\t\t\t</span>\n\n\t\t\t</div>\n\t\t</div>\n\t</div>\n</li>'

		return HTMLOutput

# Zmienna przechowująca wszystkie obiekty znalezisk, inicjalnie pusta
EntriesList = []

def printEntries():
	for Entry in EntriesList:
		print(str(Entry))

class DigHTMLParser(HTMLParser):
	inside_entry = 0
	processing_tags = 0

	def process_data(self, tag, data):
		### przychodzące dane interesują nas tylko w trybie analizy konkretnego ogłoszenia
		if self.inside_entry != 1:
			return

		### odrzucanie wartości, które są do niczego niepotrzebne i psują interpretację
		if tag == "" and (re.match(re.compile("^(wykop|@|#|\+[0-9]+ inne|[\s]+opublikowany[\s]+|\+1 inny)$"), data) != None or re.match(re.compile("^[\s]+$"), data) != None):
                        return	
		if tag == "a" and (re.match(re.compile("^(.*https://www.wykop.pl/rejestracja/.*)$"), str(data)) != None):
                        return	

		### jeśli otrzymaliśmy tylko tekst - poza tagiem - uzupełniamy odpowiednie atrybuty obiektu
		if tag == '':
			# czy zajmujemy się obecnie tagami
			if self.processing_tags == 1:
				if EntriesList[-1].extSite != "" and EntriesList[-1].author != "":
					EntriesList[-1].tags.append(data)
				else:
					if EntriesList[-1].author == "":
						EntriesList[-1].author = data
					elif EntriesList[-1].extSite == "":
						EntriesList[-1].extSite = data
			else:
				# uzupełniamy atrybuty
				if EntriesList[-1].upvotes == "":
					EntriesList[-1].upvotes = data
				elif EntriesList[-1].lead == "":
					EntriesList[-1].lead = str(data).strip()
				elif EntriesList[-1].text == "":
					EntriesList[-1].text = str(data).strip()
				elif EntriesList[-1].comments == "":
					EntriesList[-1].comments = str(data).strip()
				elif EntriesList[-1].dateMinsAgo == "":
					EntriesList[-1].dateMinsAgo = str(data).strip()

			return

		### jeśli otrzymaliśmy tag to musimy go zinterpretować
		# iteracja po strukturze data - są to argumenty tagu
		for attr in data:
			# poniższe rodzaje opcji mają argumenty - trzeba je wyłuskać
			if tag == "a":
				if attr[0] == "href" and EntriesList[-1].intUrl == "":
					EntriesList[-1].intUrl = attr[1]
			if tag == "img":
				if attr[0] == "src" and EntriesList[-1].imgPrevUrl == "":
					EntriesList[-1].imgPrevUrl = attr[1]
				elif attr[0] == "data-original" and EntriesList[-1].imgPrevUrl == "":
					EntriesList[-1].imgPrevUrl = attr[1]
				elif attr[0] == "alt" and EntriesList[-1].imgPrevAlt == "":
					EntriesList[-1].imgPrevAlt = attr[1]
			if tag == "div":
				if EntriesList[-1].eid == "" and attr[0] == "data-id":
					EntriesList[-1].eid = attr[1]
			if tag == "time":
				if EntriesList[-1].dateSimple == "" and attr[0] == "title":
					EntriesList[-1].dateSimple = attr[1]
				if EntriesList[-1].dateExtend == "" and attr[0] == "datetime":
					EntriesList[-1].dateExtend = attr[1]
		if tag == "a":
			extMatched = 0
			for attr in data:
				if attr[0] == "class" and attr[1] == "affect":
					extMatched = 1
				if attr[0] == "href" and extMatched == 1 and EntriesList[-1].extUrl == "":
					EntriesList[-1].extUrl = attr[1]


	def handle_starttag(self, tag, attrs):
		### każdy otwarty tag analizujemy
		# jeśli tagiem jest div, to analizujemy szczególnie mocno
		if tag == "li":
			for attr in attrs:
				# jeśli nowy obiekt li należy do odpowiedniej klasy, to wchodzimy w tryb ogłoszenia
				# ustawiamy zmienną oraz tworzymy nowy obiekt reprezentujący ogłoszenie
				if len(attr) == 2 and attr[0] == "class" and re.match(re.compile(entryClass, flags=re.IGNORECASE), attr[1]):
					newEntry = Entry()
					EntriesList.append(newEntry)
					self.inside_entry = 1
					if hotModifier in attr[1]:
						EntriesList[-1].hotOrNot = hotModifier
		# jeśli tagiem jest div z tagami znaleziska, to wchodzimy w odpowiedni tryb
		if self.inside_entry == 1 and tag == "div":
			for attr in attrs:
				if len(attr) == 2 and attr[0] == "class" and attr[1] == tagClass:
					self.processing_tags = 1
		### a generalnie przekazujemy dane do interpretacji
		self.process_data(tag, attrs)
					
	def handle_endtag(self, tag):
		### jeśli zamykamy tag li, to zerujemy stan inside_entry - wychodzimy z trybu analizy konkretnego ogłoszenia
		if tag == "li":
			self.inside_entry = 0
		### jeśli zamykamy tag div i jesteśmy w trybie dodawania tagów, to opuszczamy ten tryb
		if self.inside_entry == 1 and tag == "div" and self.processing_tags == 1:
			self.processing_tags = 0

	def handle_data(self, data):
		### przekazujemy dane do interpretacji
		self.process_data('', data)

# Instancjalizacja klasy analizatora HTTP
http = httplib2.Http()

# Parametry żądania
content = http.request("https://www.wykop.pl/", method="GET")[1]
page = 2
while page <= dig_numPages:
        content += http.request("https://www.wykop.pl/strona/" + str(page), method="GET")[1]
        page += 1

# Wywołujemy parse'owanie
parser = DigHTMLParser()
parser.feed(content.decode())

# Wypisujemy stały header strony
header = open("inc/header.html", "r")
print(header.read())
# Wypisujemy treść ogłoszeń w HTML
printEntries()
# Wypisujemy stały footer strony
footer = open("inc/footer.html", "r")
print(footer.read())
