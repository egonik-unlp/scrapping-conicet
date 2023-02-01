#! /usr/bin/env python

import pandas as pd
import requests 
from bs4 import BeautifulSoup
import os
import re
from scholarly import scholarly
from scholarly import ProxyGenerator
import json
from data_institutos import main as get_data_institutos

pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)
BREAKPOINT = None

AFFILIATION_SHORT_NAME = "INIFTA".lower()
AFFILIATION_LONG_NAME = "Instituto de Investigaciones Fisicoquímicas Teóricas y Aplicadas".lower()
OTHER_AFFILIATION_NAME = "Universidad Nacional de La Plata".lower()
CHECKPOINT = 10 ## Prints data to see how we are doing
INSTITUTO = "INIFTA"
FILENAME_DATA_INSTITUTOS = "info_institutos.json"

if os.path.exists(FILENAME_DATA_INSTITUTOS):
	with open(FILENAME_DATA_INSTITUTOS) as file:
		data = json.load(file)
else: 
	data_institutos = get_data_institutos()



def get_institute_personnel(INSTITUTO:str) -> list: 

	url_instituto = data_institutos.get(INSTITUTO, "").upper()
	if url_instituto == "":
		print("El instituto {} no existe o lo escribiste mal".format(INSTITUTO))
	response = requests.get("https://www.conicet.gov.ar/new_scp/detalle.php?keywords={}&id=05425&inst=yes&rrhh=yes".format(INSTITUTO))
	soup = BeautifulSoup(response.content, features = "lxml")
	nombres_personas = []
	escalafones = soup.find_all(class_ = "escalafon")
	for  escalafon in escalafones:
		personas = escalafon.find_all(class_ =  "contenido_item")
		for nombre_de_autor in personas:
			
			try:	
				nda = nombre_de_autor.get_text() 
				p = nda.split(",")
				x = [t.strip().lower() for t in p]
				x.reverse()
				name = " ".join(x)
				assert len(x) == 2
				nombres_personas.append(name)
			except AssertionError:
				print("No tuve exito con {}".format("".join(nda))) 
				continue
			except TypeError:
				continue
	return nombres_personas



def search_for_author(search_query, data):
	first_author_result = next(search_query)
	CONDITION_1 = AFFILIATION_SHORT_NAME  in first_author_result["affiliation"].lower()
	CONDITION_2 = AFFILIATION_LONG_NAME   in first_author_result["affiliation"].lower()
	CONDITION_3 = OTHER_AFFILIATION_NAME  in first_author_result["affiliation"].lower()
	CONDITION_4 = AFFILIATION_SHORT_NAME  in first_author_result["email_domain"].lower()

	while not( CONDITION_1 or  CONDITION_2 or CONDITION_3 or CONDITION_4):
		first_author_result = next(search_query)
	data_author = scholarly.fill(first_author_result, ["basics", "counts"])
	data[first_author_result["name"]] = data_author
	return data




def get_data(nombres_personas : list, BREAKS: int) -> dict:
	data = {}
	for n,author in enumerate(nombres_personas[:BREAKS]):
		search_query = scholarly.search_author(author)
		
		try:
			data = search_for_author(search_query, data)
			
		except StopIteration:
			try:
				all_names_of_author = author.split(" ")
				tryname = " ".join([all_names_of_author[0], all_names_of_author[-1]])
				search_query = scholarly.search_author(tryname)
				data = search_for_author(search_query, data)
			except StopIteration:
				print("pase por aca con {}".format(tryname))
				data[author] = {}

		if n % 10 == 0:
			pg = ProxyGenerator()
			pg.FreeProxies()
			scholarly.use_proxy(pg)
		if n == CHECKPOINT:
			print(data)
	return data



def main():
	nombres_personas = get_institute_personnel()
	BREAKS = BREAKPOINT or len(nombres_personas)
	print(nombres_personas)
	print(len(nombres_personas))
	data = get_data(nombres_personas, BREAKS)

	with open("datos_investigadores_inifta.json", "w") as file:
		json.dump(data, file)	

	pd.DataFrame(data).to_csv("datos_personal_{}.csv".format(INSTITUTO))
	return data


if __name__ == "__main__": 
	data = main()
	

