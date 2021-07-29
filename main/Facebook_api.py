import mysql.connector
import pandas as pd
import numpy as np
import pymysql
import requests
from datetime import datetime
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
         
        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])
            
        database = (api_request(database['paging']['next']))
            
    
    else:  
        
        for index in range(len(database['data'])):
            
            idlist.append(database['data'][index]['id'])

        print("{} posts coletados".format(len(idlist)))
        return idlist 

def get_database(idlist):

    tabela = []

    for loopid in idlist:       
        thisid = []

        loopdata = api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=likes.summary(true).limit(0)%2Ccomments.summary(total_count).limit(0)%2Cshares%2Cpermalink_url%2Cid%2Cmessage%2Ccreated_time%2Cfull_picture&access_token="+token)
        loopmetrics = api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=post_impressions%2Cpost_impressions_paid%2Cpost_impressions_organic%2Cpost_impressions_unique%2Cpost_impressions_paid_unique%2Cpost_impressions_organic_unique%2Cpost_video_views_10s%2Cpost_video_views_10s_paid&access_token="+token)
        
        
        if "message" in loopdata:

            thisid.append(loopdata['created_time']) if "created_time" in loopdata else thisid.append(0)
            thisid.append(loopdata['message']) if "message" in loopdata else thisid.append(0)
            thisid.append(loopdata['likes']['summary']['total_count']) if "likes" in loopdata else thisid.append(0)
            thisid.append(loopdata['comments']['summary']['total_count']) if "comments" in loopdata else thisid.append(0)
            thisid.append(loopdata['shares']['count']) if "shares" in loopdata else thisid.append(0)

            for loop in range(8):

                thisid.append(loopmetrics['data'][loop]['values'][0]['value']) 

            thisid.append(loopdata['id']) if "id" in loopdata else thisid.append(0)
            thisid.append(loopdata['permalink_url']) if "permalink_url" in loopdata else thisid.append(0)
            thisid.append(loopdata['full_picture']) if "full_picture" in loopdata else thisid.append(0)

            tabela.append(thisid)

    tabela = pd.DataFrame(tabela, columns=["Data","Texto","Reações","Comentários","Compartilhamentos","Impressão","Impressão Paga","Impressão Orgânica","Alcance","Alcance Pago","Alcance Orgânico","Visualizações 10s Total","Visualizações 10s Pagas","ID","Link","Link da Imagem"])

    tabela.insert(2,"Classificação","")
    tabela.insert(3,"Marca","")
    tabela.insert(15,"Valor Gasto","")
    
    return tabela
    
def export_excel(database,nome):

    output = nome + ".xlsx"
    database.to_excel(output)
    return print('Arquivo exportado com o nome {}'.format(output))  

tabela = get_database(get_ids('01/07/2021','28/07/2021'))
export_excel(tabela,'Facebook - Julho 21')