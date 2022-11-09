#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import scrapy
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

import re

# guardar el dataset en format csv
def store_dataset(filename, ds):
    ds.to_csv(filename, index=None);


# In[22]:


def html_parser(URL: str):
    req = requests.get(URL)
    html = BeautifulSoup(req.text, 'html.parser')
    return html

def tag_a_indicadors(URL: str) -> list:
    html = html_parser(URL)
    indicadors = html.find('a',{'class':'dropdown-toggle'}).get('href')
    html = html_parser(indicadors)
    tag_a = html.find_all('a')
    return tag_a 

def url_indicador(URL: str,indicadors: list, indicador: str) -> str:
    for i, a in enumerate(indicadors):
        if(a.text==indicador):
            indi_url = a.get('href')
    return URL+indi_url

def busca_urls_pais(URL: str, indicador: str):
    p = []
    names = []
    tag_a = tag_a_indicadors(URL)
    indicador_url = url_indicador(URL, tag_a, indicador)
    tag_a = html_parser(indicador_url).find_all('a')
    #obtenim url del pais
    for i, a in enumerate(tag_a):
        if(' [+]' in a.text):
            pais_url = a.get('href')
            pais = a.text.replace(' [+]', '')
            names.append(pais)
            p.append(URL+pais_url)
    
    ret = []
    paisos = []
    cont = 0
    #obtenim tots els anys
    for precios_pais_url in p:
        name = names[cont]
        html = html_parser(precios_pais_url)
        URL_list = [precios_pais_url]
        Paisos_list = [name]
        while len(set(URL_list))==len(URL_list):
            url = html.find('table').find('a').get('href')
            req = requests.get(url)
            html = BeautifulSoup(req.text, "html.parser")
            URL_list = URL_list + [url]
            Paisos_list = Paisos_list + [name]
            # Treiem els dos últims per què l'últim torna a ser l'any actual(per defecte) i el penúltim també
            # és a dir, si posem un any que no existeix et torna a l'any actual
        ret.extend(URL_list[:-2])
        paisos.extend(Paisos_list[:-2])
        cont = cont + 1 
        df = pd.DataFrame()
        df["url"] = ret
        df["pais"] = paisos
    return taula_preus(df["url"], df["pais"])

def busca_url_internacional(URL: str, indicador: str) -> list:
    taula_total = pd.DataFrame()
    tag_a = tag_a_indicadors(URL)
    indicador_url = url_indicador(URL, tag_a, indicador)
    html = html_parser(indicador_url)

    year = datetime.date.today().year # default value
    
    while year > 2002: # nomes hi ha dades fins 2003, si seguim clickant links es crea circularitat aixi que parem nosaltres...
        dates = []
        preu_eur = []
        preu_dol = []
        taula_tmp = pd.DataFrame()
        url = html.find_all('table',{'id':'tb1_1463'})
        url = url[1].find('tbody')
        # les dues taules de la pagina tenen el mateix id... volem la de la dreta que té dades mensuals
        rows = url.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if(str(year) in cols[0].text): # quan tenim un any a mitges posa les dades del anterior. Aquestes les volem saltar.
            	dates.append(cols[0].text)
            	preu_dol.append(cols[1].text) 
            	preu_eur.append(cols[2].text)
            if('Enero' in cols[0].text):
            	year = int(cols[0].text[-4:])
        year = year - 1
        taula_tmp["Fecha"] = dates
        taula_tmp["Precio dolar"] = preu_dol
        taula_tmp["Precio euro"] = preu_eur
        taula_total = pd.concat([taula_total, taula_tmp], axis = 0).reset_index(drop=True)        
        # iterem al seguent any	
        url_new = indicador_url + '?anio=' + str(year)
        print(url_new)
        html = html_parser(url_new)

    # Treiem l'últim torna a ser l'últim(per defecte)
    return taula_total#URL_list[:-1]

def taula_preus(URL: list, PAIS: list) -> pd.DataFrame:
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
            dia = datetime.datetime.strptime(fecha.get('data-value'), '%Y-%m-%d')
            dies = dies + [dia]
        # guardem a la taula
        taula[cap[0].text] = dies  
        # obtenim el preu dels derivats
        preus = html.find_all('td',{'class':'numero'})
        for j, preu in enumerate(preus):
            pp = preu.get('data-value')
            if (pp == ''):
                pr = None
            else:     
                pr = float(pp)
            pr_g = pr_g + [pr]
        # generem llista per cada derivat i guardem a la taula
        for j in range(0,6):
            for k in range(j,len(pr_g),6):
                derivats = derivats + [pr_g[k]]
            taula[cap[j+1].text] = derivats
            derivats = []
        # agrupem cada taula 
        taula['Pais'] = PAIS[i]
        taula_total = pd.concat([taula_total, taula], axis = 0).reset_index(drop=True)
    return taula_total


# In[23]:


URL = "https://www.datosmacro.com"
data = busca_urls_pais(URL,'Precios al consumidor de productos petrolíferos')
store_dataset('dades.csv', data)


# In[ ]:
data = busca_url_internacional(URL, 'Precio del petróleo OPEP')
store_dataset("barrils.csv", data)


