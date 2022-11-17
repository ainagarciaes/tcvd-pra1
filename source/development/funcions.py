import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
#####################################
def html_parser(URL: str):
    req = requests.get(URL)
    html = BeautifulSoup(req.text, 'html.parser')
    return html
#####################################
def tag_a_indicadors(URL: str) -> list:
    html = html_parser(URL)
    indicadors = html.find('a',{'class':'dropdown-toggle'}).get('href')
    html = html_parser(indicadors)
    tag_a = html.find_all('a')
    return tag_a 
#####################################
def url_indicador(URL: str,indicadors: list, indicador: str) -> str:
    for i, a in enumerate(indicadors):
        if(a.text==indicador):
            indi_url = a.get('href')
    return URL+indi_url
#####################################
def busca_url_pais(URL: str, indicador: str, pais: str) -> list:
    tag_a = tag_a_indicadors(URL)
    indicador_url = url_indicador(URL, tag_a, indicador)
    tag_a = html_parser(indicador_url).find_all('a')
    #obtenim url del pais
    for i, a in enumerate(tag_a):
        if(a.text==pais+' [+]'):
            pais_url = a.get('href')
    precios_pais_url = URL+pais_url
    #obtenim tos els anys
    html = html_parser(precios_pais_url)
    URL_list = [precios_pais_url]
    while len(set(URL_list))==len(URL_list):
        url = html.find('table').find('a').get('href')
        req = requests.get(url)
        html = BeautifulSoup(req.text, "html.parser")
        URL_list = URL_list + [url]
    # Treiem els dos últims per què l'últim torna a ser l'any actual(per defecte) i el penúltim també
    # és a dir, si posem un any que no existeix et torna a l'any actual
    return URL_list[:-2]
#################################################################
def busca_url_internacional(URL: str, indicador: str) -> list:
    tag_a = tag_a_indicadors(URL)
    indicador_url = url_indicador(URL, tag_a, indicador)
    html = html_parser(indicador_url)
    URL_list = [indicador_url]
    while len(set(URL_list))==len(URL_list):
        url = html.find('table',{'class':'table tabledat table-striped table-condensed table-hover'}).find('a').get('href')
        html = html_parser(url)
        URL_list = URL_list + [url]
    # Treiem l'últim torna a ser l'últim(per defecte)
    return URL_list[:-1]
#################################################################   
def taula_preus(URL: list) -> pd.DataFrame:
    taula_total = pd.DataFrame()
    # per cada url en la llista URL obtenim la taula de preus dels derivats del petroli
    for i, url in enumerate(URL):
        taula = pd.DataFrame()
        dies = []
        pr_g= []
        derivats = []
        html = html_parser(url)        
        # obtenim el nom dels atributs
        cap = html.find_all('th')
        # obtenim l'atribut fecha i convertim a datetime
        fechas = html.find_all('td',{'class':'fecha'})
        for j, fecha in enumerate(fechas):
            dia = datetime.strptime(fecha.get('data-value'), '%Y-%m-%d')
            dies = dies + [dia]
        # guardem a la taula
        taula[cap[0].text] = dies  
        # obtenim el preu dels derivats
        preus = html.find_all('td',{'class':'numero'})
        for j, preu in enumerate(preus):
            pr = float(preu.get('data-value'))
            pr_g = pr_g + [pr]
        # generem llista per cada derivat i guardem a la taula
        for j in range(0,6):
            for k in range(j,len(pr_g),6):
                derivats = derivats + [pr_g[k]]
            taula[cap[j+1].text] = derivats
            derivats = []
        # agrupem cada taula 
        taula_total = pd.concat([taula_total, taula], axis = 0).reset_index(drop=True)
    
    return taula_total
##########################################################
