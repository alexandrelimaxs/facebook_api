import pandas as pd
import numpy as np
import requests
from datetime import datetime
import math
import json

token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"

def api_request(url):
    res = requests.get(url)
    return json.loads(res.text)

def filtro_data(database,data_inicial,data_final):
	idlist_filtro = []

	for loop in range(len(database['data'])):
		print('filtering timestamp {}'.format(database['data'][loop]['timestamp']))
		if data_inicial < database['data'][loop]['timestamp'] < data_final:
			print('adding post id')
			idlist_filtro.append(database['data'][loop]['id'])
		elif database['data'][loop]['timestamp'] < data_inicial:
			break

			
	return idlist_filtro

def date_to_unix(data):

	dataf = data.split('/')
	dataf = [int(x) for x in dataf]
	dataf = datetime(dataf[2],dataf[1],dataf[0])
	return	datetime.timestamp(dataf)

def get_ids_instagram(inicio, fim):

	data_inicial = date_to_unix(inicio)
	data_final = date_to_unix(fim)

	print("Inicial:{}".format(data_inicial))
	
	print("Final:{}".format(data_final))


	idlist = []
	request_url = "https://graph.facebook.com/v11.0/17841402122853134/media?fields=id%2Ctimestamp&date_format=U&access_token="+token
	
	database = api_request(request_url) 							

	while database['data'][-1]['timestamp'] > data_final: 							
		print(database['data'][-1]['timestamp'])
		database = api_request(database['paging']['next'])
		

	else:

		while database['data'][-1]['timestamp'] > data_inicial:							# enquanto a data do ultimo item do request for posterior ao INICIO do intervalo, coleta IDS

			idlist = idlist + filtro_data(database,data_inicial,data_final)
			database = api_request(database['paging']['next']) 					# substitui database antiga pela nova

		else:														# se o ultimo item passar o INICIO do intervalo, varrer database buscando os restantes e para o loop

			idlist = idlist + filtro_data(database,data_inicial,data_final)
			return idlist

		




	 


database = (get_ids_instagram('01/06/2021','06/07/2021'))

print(database)
