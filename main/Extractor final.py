import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json

class banco_de_dados_facebook:

    def api_request(self, url):
        res = requests.get(url)
        return json.loads(res.text)

    def date_to_unix_str(self, data):

        dataf = data.split('/')
        dataf = [int(x) for x in dataf]
        dataf = datetime(dataf[2],dataf[1],dataf[0])
        
        return  str(datetime.timestamp(dataf))[:-2]
    
    def get_ids_facebook(self, inicio, fim):
    
        data_inicial = self.date_to_unix_str(inicio)
        data_final = self.date_to_unix_str(fim)

        idlist = []
        request_url = "https://graph.facebook.com/v11.0/me/posts?fields=id&date_format=U&since="+data_inicial+"&until="+data_final+"&access_token="+self.token
        
        database = self.api_request(request_url)
        
        while "next" in database['paging']:
            
            for index in range(len(database['data'])):
                
                idlist.append(database['data'][index]['id'])
                
            database = (self.api_request(database['paging']['next']))
                
        
        else:  
            
            for index in range(len(database['data'])):
                
                idlist.append(database['data'][index]['id'])

            return idlist
    
    def extract_facebook(self, inicio_intervalo, fim_intervalo):

        idlist = self.get_ids_facebook(inicio_intervalo, fim_intervalo)

        tabela = []

        for loopid in idlist:       
            thisid = []

            loopdata = self.api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=likes.summary(true).limit(0)%2Ccomments.summary(total_count).limit(0)%2Cshares%2Cpermalink_url%2Cid%2Cmessage%2Ccreated_time%2Cfull_picture&access_token="+self.token)
            loopmetrics = self.api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=post_impressions%2Cpost_impressions_paid%2Cpost_impressions_organic%2Cpost_impressions_unique%2Cpost_impressions_paid_unique%2Cpost_impressions_organic_unique%2Cpost_video_views_10s%2Cpost_video_views_10s_paid&access_token="+self.token)
            
            
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

    def __init__(self, inicio, fim):

        self.token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"
        
        self.dados = self.extract_facebook(inicio,fim)

class banco_de_dados_instagram:

    def api_request(self, url):
        res = requests.get(url)
        return json.loads(res.text)
    
    def date_to_unix(self, data):

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


teste = banco_de_dados('01/07/2021','03/07/2021')

print(teste.dados)