#! /usr/bin/env python

import pandas as pd
import requests 
from bs4 import BeautifulSoup
import re
import json


def main():

	url = "https://red.conicet.gov.ar/nomina-y-mapa-institucional/"
	html = requests.get(url).content
	soup = BeautifulSoup(html, features = "lxml")
	sigla_ue = soup.find_all(class_ = "sigla_ue") 
	nombre_ue = soup.find_all(class_ = "nombre_ue")
	data_ue = soup.find_all(class_ = "ver_mas_ue")
	try:
		assert len(sigla_ue) == len(nombre_ue) == len(data_ue)
	except AssertionError:
		print("Se me rompio el codigo, seguro cambio la pagina de conicet")
	data = {sigla.get_text() : data.find("a").get("href") for sigla,data in zip(sigla_ue, data_ue)}

	with open("info_institutos.json", "w") as file:
		json.dump(data, file)
	return data

if __name__ ==	"__main__":
	data = main()