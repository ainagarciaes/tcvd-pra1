from funcions import*

URL = "https://www.datosmacro.com"
sp = busca_url_pais(URL,'Precios al consumidor de productos petrolíferos','España')
taula_sp = taula_preus(sp)
fr = busca_url_pais(URL,'Precios al consumidor de productos petrolíferos','Francia')
taula_fr = taula_preus(fr)
print(taula_sp)
print(taula_fr)
