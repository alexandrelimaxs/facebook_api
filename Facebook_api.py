import pandas as pd
import numpy as np
import requests
from datetime import datetime
import math
import json

token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"
current_url = "https://graph.facebook.com/v11.0/me/posts?fields=id&date_format=U&since=1625108400&access_token="+token

# --------------------------------------------------

idlist = []

def api_request(url):
    res = requests.get(url)
    return json.loads(res.text)

def get_ids(dados):

    for index in range(len(dados['data'])):
        idlist.append(dados['data'][index]['id'])
    
    if "next" in dados['paging']:       #condicional para realizar recursiva caso haja uma próxima página
        get_ids(api_request(dados['paging']['next']))

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


# database = api_request(current_url)
# get_ids(database)
# database = get_database(idlist)
# export_excel(database, "Planilha Teste")




