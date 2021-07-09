import pandas as pd
import numpy as np
import requests
from datetime import datetime
import math
import json

token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"
# current_url = "https://graph.facebook.com/v11.0/me/posts?fields=id&date_format=U&since=1625108400&access_token="+token

# --------------------------------------------------



def api_request(url):       # função que chama o request e converte em json
    res = requests.get(url)
    return json.loads(res.text)

def date_to_unix(data):

    dataf = data.split('/')
    dataf = [int(x) for x in dataf]
    dataf = datetime(dataf[2],dataf[1],dataf[0])
    return  datetime.timestamp(dataf)

def get_ids(inicio, fim):
    
    data_inicial = date_to_unix(inicio)
    data_final = date_to_unix(fim)
    data_inicial = str(data_inicial)
    data_final = str(data_final)
    data_inicial = data_inicial[:-2]
    data_final = data_final[:-2]

    idlist = []
    request_url = "https://graph.facebook.com/v11.0/me/posts?fields=id&date_format=U&since="+data_inicial+"&until="+data_final+"&access_token="+token
    
    database = api_request(request_url)
    
    
    while "next" in database['paging']:

        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])

        database = (api_request(database['paging']['next']))
            
    
    else:  
        
        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])

        return idlist

    

def get_database(idlist):   #função que pega a lista de ids, coleta os dados de cada id, escreve uma matriz e retorna o DataFrame em Pandas

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

def export_excel(database,nome):    #função que coleta o nome desejado pra planilha, exporta para excel e retorna um print
    output = nome + ".xlsx"
    database.to_excel(output)
    return print('Arquivo exportado com o nome {}'.format(output))  



print(get_ids('01/06/2021','06/07/2021'))

