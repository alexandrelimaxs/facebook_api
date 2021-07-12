import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json

token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"

def api_request(url):
    res = requests.get(url)
    return json.loads(res.text)

def date_to_unix(data):

    dataf = data.split('/')
    dataf = [int(x) for x in dataf]
    dataf = datetime(dataf[2],dataf[1],dataf[0])
    return	datetime.timestamp(dataf)

def filtro_data(database,data_inicial,data_final):

    idlist_filtro = []

    for loop in range(len(database['data'])):

        if int(data_inicial) < database['data'][loop]['timestamp'] < int(data_final):
            
            idlist_filtro.append(database['data'][loop]['id'])

        elif database['data'][loop]['timestamp'] < data_inicial:

            break

            
    return idlist_filtro

def get_ids_instagram(inicio, fim):

    data_inicial = date_to_unix(inicio)
    data_final = date_to_unix(fim)

    idlist = []
    request_url = "https://graph.facebook.com/v11.0/17841402122853134/media?fields=id%2Ctimestamp&date_format=U&access_token="+token
    
    database = api_request(request_url) 							

    while database['data'][-1]['timestamp'] > data_final: 							
        
        database = api_request(database['paging']['next'])
        

    else:

        while database['data'][-1]['timestamp'] > data_inicial:							# enquanto a data do ultimo item do request for posterior ao INICIO do intervalo, coleta IDS

            idlist = idlist + filtro_data(database,data_inicial,data_final)
            database = api_request(database['paging']['next']) 					# substitui database antiga pela nova

        else:														# se o ultimo item passar o INICIO do intervalo, varrer database buscando os restantes e para o loop

            idlist = idlist + filtro_data(database,data_inicial,data_final)
            return idlist

def get_database(idlist):

    tabela = []

    for loopid in idlist:
        
        thisid = []
        
        loopdata = api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=caption%2Ctimestamp%2Cmedia_product_type%2Cmedia_type%2Clike_count%2Ccomments_count%2Cid%2Cpermalink%2Cmedia_url&access_token="+token)
        loopmetrics = api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=reach%2Cimpressions%2Csaved&access_token="+token)
        
        thisid.append(loopdata['timestamp']) if "timestamp" in loopdata else thisid.append(0)
        thisid.append(loopdata['caption']) if "caption" in loopdata else thisid.append(0)
        # thisid.append(loopdata['media_product_type']) if "media_product_type" in loopdata else thisid.append(0)
        thisid.append(loopdata['media_type']) if "media_type" in loopdata else thisid.append(0)
        thisid.append(loopdata['like_count']) if "like_count" in loopdata else thisid.append(0)
        thisid.append(loopdata['comments_count']) if "comments_count" in loopdata else thisid.append(0)
        for loop in range(3):
            thisid.append(loopmetrics['data'][loop]['values'][0]['value'])
        if loopdata['media_type'] == "VIDEO":
            videorequest = api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=video_views&access_token="+token)
            thisid.append(videorequest['data'][0]['values'][0]['value'])
        else:
            thisid.append(0)
        thisid.append(loopdata['id']) if "id" in loopdata else thisid.append(0)
        thisid.append(loopdata['permalink']) if "permalink" in loopdata else thisid.append(0)
        thisid.append(loopdata['media_url']) if "media_url" in loopdata else thisid.append(0)
        
        tabela.append(thisid)

    return pd.DataFrame(tabela, columns=["Data","Texto","Tipo do Post","Likes","Comentários","Alcance","Impressões","Salvos","Visualizações","ID","Link","Link da Imagem"])   

def export_excel(database,nome):
    output = nome + ".xlsx"
    database.to_excel(output)
    return print('Arquivo exportado com o nome {}'.format(output))  

database = get_database(get_ids_instagram('01/06/2021','01/07/2021'))
export_excel(database, "Instagram - Junho 21")


