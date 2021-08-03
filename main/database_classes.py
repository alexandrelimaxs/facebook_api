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
        
        self.planilha = self.extract_facebook(inicio,fim)

class banco_de_dados_instagram:

    def api_request(self, url):
        res = requests.get(url)
        return json.loads(res.text)
    
    def date_to_unix(self, data):

        dataf = data.split('/')
        dataf = [int(x) for x in dataf]
        dataf = datetime(dataf[2],dataf[1],dataf[0])
        
        return	datetime.timestamp(dataf)

    def filtro_data(self, database,data_inicial,data_final):

        idlist_filtro = []

        for loop in range(len(database['data'])):

            if int(data_inicial) < database['data'][loop]['timestamp'] < int(data_final):
                
                idlist_filtro.append(database['data'][loop]['id'])

            elif database['data'][loop]['timestamp'] < data_inicial:

                break

            
        return idlist_filtro

    def get_ids_instagram(self, inicio, fim):

        data_inicial = self.date_to_unix(inicio)
        data_final = self.date_to_unix(fim)

        idlist = []
        request_url = "https://graph.facebook.com/v11.0/17841402122853134/media?fields=id%2Ctimestamp&date_format=U&access_token="+self.token
        
        database = self.api_request(request_url) 							

        while database['data'][-1]['timestamp'] > data_final: 							
            
            database = self.api_request(database['paging']['next'])
            

        else:

            while database['data'][-1]['timestamp'] > data_inicial:							# enquanto a data do ultimo item do request for posterior ao INICIO do intervalo, coleta IDS

                idlist = idlist + self.filtro_data(database,data_inicial,data_final)
                database = self.api_request(database['paging']['next']) 					# substitui database antiga pela nova

            else:														# se o ultimo item passar o INICIO do intervalo, varrer database buscando os restantes e para o loop

                idlist = idlist + self.filtro_data(database,data_inicial,data_final)
                return idlist

    def extract_database(self, inicio_intervalo, fim_intervalo):

        idlist = self.get_ids_instagram( inicio_intervalo, fim_intervalo)

        tabela = []

        for loopid in idlist:
            
            thisid = []
            
            loopdata = self.api_request("https://graph.facebook.com/v11.0/"+loopid+"?fields=caption%2Ctimestamp%2Cmedia_product_type%2Cmedia_type%2Clike_count%2Ccomments_count%2Cid%2Cpermalink%2Cmedia_url&access_token="+self.token)
            loopmetrics = self.api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=reach%2Cimpressions%2Csaved&access_token="+self.token)
            
            thisid.append(loopdata['timestamp']) if "timestamp" in loopdata else thisid.append(0)
            thisid.append(loopdata['caption']) if "caption" in loopdata else thisid.append(0)
            thisid.append(loopdata['media_type']) if "media_type" in loopdata else thisid.append(0)
            thisid.append(loopdata['like_count']) if "like_count" in loopdata else thisid.append(0)
            thisid.append(loopdata['comments_count']) if "comments_count" in loopdata else thisid.append(0)
            for loop in range(3):
                thisid.append(loopmetrics['data'][loop]['values'][0]['value'])
            if loopdata['media_type'] == "VIDEO":
                videorequest = self.api_request("https://graph.facebook.com/v11.0/"+loopid+"/insights?metric=video_views&access_token="+self.token)
                thisid.append(videorequest['data'][0]['values'][0]['value'])
            else:
                thisid.append(0)
            thisid.append(loopdata['id']) if "id" in loopdata else thisid.append(0)
            thisid.append(loopdata['permalink']) if "permalink" in loopdata else thisid.append(0)
            thisid.append(loopdata['media_url']) if "media_url" in loopdata else thisid.append(0)
            
            tabela.append(thisid)

        tabela = pd.DataFrame(tabela, columns=["Data","Texto","Tipo da Mídia","Likes","Comentários","Alcance Orgânico","Impressões Orgânico","Salvos","Visualizações","ID","Link","Link da Imagem"])   

        tabela.insert(3,"Classificação","")
        tabela.insert(4,"Marca","")
        tabela.insert(7,"Alcance","")
        tabela.insert(8,"Alcance Pago","")
        tabela.insert(10,"Impressão","")
        tabela.insert(11,"Impressão Pago","")
        tabela.insert(15,"Valor Gasto","")

        return tabela
    
    def __init__(self, inicio, fim):

        self.token = "EAADsWrQWaGABAGyLVcZB0KK82UrXb2L1buoAkOdu7NZAw7eabJ6jDAeSVj69e8HK5EwUQaIQZCiXhPMbleNUGfP5CDFF1790rOWDrPotjrAxuh51vID63NyLE0WNeHvHd5ZAE90xZC9jY3zZCazZCZAPnVqAuZBe4zBgG0pIZAQ6vTZAXMKLOeqJzSY"

        self.planilha = self.extract_database(inicio, fim)

    def __new__(cls):
        return self.planilha
    
dados = banco_de_dados_instagram('01/07/2021', '03/07/2021')

print(dados)

