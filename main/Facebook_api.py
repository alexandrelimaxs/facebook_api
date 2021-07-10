import pandas as pd
import numpy as np
import requests
from datetime import datetime
import math
import json

token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"

# --------------------------------------------------



def api_request(url):
    res = requests.get(url)
    return json.loads(res.text)

def date_to_unix_str(data):

    dataf = data.split('/')
    dataf = [int(x) for x in dataf]
    dataf = datetime(dataf[2],dataf[1],dataf[0])
    
    return  str(datetime.timestamp(dataf))[:-2]

def get_ids(inicio, fim):
    
    data_inicial = date_to_unix_str(inicio)
    data_final = date_to_unix_str(fim)


    idlist = []
    request_url = "https://graph.facebook.com/v11.0/me/posts?fields=id&date_format=U&since="+data_inicial+"&until="+data_final+"&access_token="+token
    
    database = api_request(request_url)
    
    
    while "next" in database['paging']:
        print('Nova Página')
        contador = 0

        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])
            print('Id Adicionado')
            contador += 1
        print('{} ids adicionados'.format(contador))
        database = (api_request(database['paging']['next']))
            
    
    else:  
        contador = 0
        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])
            contador += 1

        print('{} ids adicionados'.format(contador))
        return idlist 

def get_database(idlist):

    tabela = []

    for loopid in idlist:       
        thisid = []

        #request dos likes, comments, shares, created time e link
        loopdata = api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=likes.summary(true).limit(0)%2Ccomments.summary(total_count).limit(0)%2Cshares%2Cpermalink_url%2Ccreated_time&access_token="+token)
        
        # condição que checa se o valor existe no dicionário do request, caso não exista, ele adiciona um valor 0
        thisid.append(loopdata['likes']['summary']['total_count']) if "likes" in loopdata else thisid.append(0)
        thisid.append(loopdata['shares']['count']) if "shares" in loopdata else thisid.append(0)
        thisid.append(loopdata['comments']['summary']['total_count']) if "comments" in loopdata else thisid.append(0)
        thisid.append(loopdata['created_time']) if "created_time" in loopdata else thisid.append(0)
        thisid.append(loopdata['permalink_url']) if "permalink_url" in loopdata else thisid.append(0)

        #adiciona valores do post do loop na tabela
        tabela.append(thisid)

    #retorna a tabela em dataframe
    return pd.DataFrame(tabela, columns=["Curtidas", "Compartilhamentos", "Comentários", "Data de Criação", "Link"])   

def export_excel(database,nome):
    output = nome + ".xlsx"
    database.to_excel(output)
    return print('Arquivo exportado com o nome {}'.format(output))  

tabela = get_database(get_ids('01/06/2021','01/07/2021'))
export_excel(tabela,'Junho - 2021')

