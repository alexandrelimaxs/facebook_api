import pandas as pd
import numpy as np
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

        loopdata = api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=likes.summary(true).limit(0)%2Ccomments.summary(total_count).limit(0)%2Cshares%2Cpermalink_url%2Cid%2Cmessage%2Ccreated_time&access_token="+token)
        loopmetrics = api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=post_reactions_by_type_total%2Cpost_impressions%2Cpost_impressions_unique%2Cpost_impressions_organic%2Cpost_impressions_organic_unique%2Cpost_impressions_paid%2Cpost_impressions_paid_unique%2Cpost_video_views_10s%2Cpost_video_views_10s_unique&access_token="+token)
        
        
        if "message" in loopdata:
            thisid.append(loopdata['created_time']) if "created_time" in loopdata else thisid.append(0)
            thisid.append(loopdata['message']) if "message" in loopdata else thisid.append(0)
            thisid.append(loopmetrics['data'][1]['values'][0]['value']) #impressao
            thisid.append(loopmetrics['data'][3]['values'][0]['value']) #impressao organica
            thisid.append(loopmetrics['data'][5]['values'][0]['value']) #impressao pago
            thisid.append(loopmetrics['data'][2]['values'][0]['value']) #alcance
            thisid.append(loopmetrics['data'][4]['values'][0]['value']) #alcance organica
            thisid.append(loopmetrics['data'][6]['values'][0]['value']) #alcance pago
            thisid.append(loopmetrics['data'][7]['values'][0]['value']) #visualizações 10s
            thisid.append(loopmetrics['data'][8]['values'][0]['value']) #visualizações 10s unicas
            thisid.append(loopmetrics['data'][9]['values'][0]['value']) #impressao viral
            thisid.append(loopmetrics['data'][10]['values'][0]['value']) #alcance viral
            thisid.append(loopmetrics['data'][11]['values'][0]['value']) #impressao  não viral
            thisid.append(loopmetrics['data'][12]['values'][0]['value']) #alcance não viral
            thisid.append(loopdata['comments']['summary']['total_count']) if "comments" in loopdata else thisid.append(0)
            thisid.append(loopdata['shares']['count']) if "shares" in loopdata else thisid.append(0)
            thisid.append(loopdata['likes']['summary']['total_count']) if "likes" in loopdata else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['like']) if "like" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['love']) if "love" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['wow']) if "wow" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['haha']) if "haha" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['sorry']) if "sorry" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopmetrics['data'][0]['values'][0]['value']['anger']) if "anger" in loopmetrics['data'][0]['values'][0]['value'] else thisid.append(0)
            thisid.append(loopdata['id']) if "id" in loopdata else thisid.append(0)
            thisid.append(loopdata['permalink_url']) if "permalink_url" in loopdata else thisid.append(0)

            tabela.append(thisid)


    #retorna a tabela em dataframe
    return pd.DataFrame(tabela, columns=["Data","Texto","Impressão","Impressão Orgânica","Impressão Paga","Alcance","Alcance Orgânica","Alcance Pago","Visualizações","Visualizações Únicas","Impressão Viral","Alcance Viral","Impressão Não Viral","Alcance Não Viral","Comentários","Shares","Reações","Likes","Amei","Wow","Haha","Triste","Grr","Id","Link"])   

def export_excel(database,nome):
    output = nome + ".xlsx"
    database.to_excel(output)
    return print('Arquivo exportado com o nome {}'.format(output))  

tabela = get_database(get_ids('28/06/2021','01/07/2021'))
export_excel(tabela,'Junho - 2021')

