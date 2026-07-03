import os
import requests
import random
import time
import logging
from supabase import create_client

# Configuración de logs limpia
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_humano(mensaje, estilo="🤖 Bot:"):
    logging.info(f"{estilo} {mensaje}")

def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://p2p.binance.com/es/trade/sell-usdt/venezuela",
        "Accept": "application/json, text/plain, */*"
    })
    return s

def buscar_mejor_tasa(banco_clave, session, ultima_tasa):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    precios = []
    
    # Navegación por páginas: para no pedir 100 resultados de golpe
    for pagina in [1, 2]:
        payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 50, "page": pagina}
        
        try:
            # Espera irregular para simular a un humano leyendo
            time.sleep(random.uniform(10, 20)) 
            res = session.post(url, json=payload, timeout=15)
            data = res.json().get("data", [])
            
            if not data: continue
                
            for a in data:
                adv = a.get("adv", {})
                precio = float(adv.get("price", 0))
                nombres = " ".join([m.get("tradeMethodName", "").lower() for m in adv.get("tradeMethods", [])])
                
                if banco_clave.lower() in nombres:
                    if 50 < precio < 5000:
                        if ultima_tasa and (precio > (ultima_tasa * 2.5) or precio < (ultima_tasa * 0.4)):
                            continue
                        precios.append(precio)
        except:
            continue
            
    return max(precios) if precios else None

def ejecutar():
    log_humano(random.choice(["Echándole un ojo al mercado...", "Revisando qué tal se mueve el P2P..."]))
    session = get_session()
    
    try:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        ultima_data = db.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        precios_previos = ultima_data[0] if ultima_data else {}
    except:
        precios_previos = {}

    bancos = {
        "binance_bdv": "venezuela", 
        "binance_pagomovil": "pago", 
        "binance_banesco": "banesco", 
        "binance_mercantil": "mercantil"
    }
    
    resultados = {}
    for col, clave in bancos.items():
        precio = buscar_mejor_tasa(clave, session, precios_previos.get(col))
        if precio:
            resultados[col] = precio
            log_humano(f"Tasa encontrada en {clave}: {precio} VES.")
            
    if resultados:
        try:
            db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
            log_humano("Reporte listo y guardado. ¡Todo al día!")
        except:
            log_humano("No pude guardar en la base de datos.")
    else:
        log_humano("El mercado parece estar tranquilo o no hay coincidencias ahora mismo.")

if __name__ == "__main__":
    ejecutar()
