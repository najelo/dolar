import os
import requests
import random
import time
import logging
from supabase import create_client
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_humano(mensaje, estilo="🤖 Bot:"): logging.info(f"{estilo} {mensaje}")

def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/126.0.0.0"})
    return s

def buscar_mejor_tasa(banco_clave, session):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    precios = []
    
    for pagina in [1, 2]:
        payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 50, "page": pagina}
        try:
            time.sleep(random.uniform(5, 10)) # Espera un poco más corta
            res = session.post(url, json=payload, timeout=15)
            data = res.json().get("data", [])
            if not data: continue
            for a in data:
                adv = a.get("adv", {})
                precio = float(adv.get("price", 0))
                nombres = " ".join([m.get("tradeMethodName", "").lower() for m in adv.get("tradeMethods", [])])
                if banco_clave.lower() in nombres:
                    precios.append(precio)
        except: continue
            
    return max(precios) if precios else None

def ejecutar():
    log_humano("Revisando mercado P2P...")
    session = get_session()
    
    bancos = {
        "binance_bdv": "venezuela", 
        "binance_pagomovil": "pago", 
        "binance_banesco": "banesco", 
        "binance_mercantil": "mercantil"
    }
    
    resultados = {}
    for col, clave in bancos.items():
        precio = buscar_mejor_tasa(clave, session)
        if precio:
            resultados[col] = precio
            log_humano(f"Tasa encontrada en {col}: {precio} VES.")
            
    if resultados:
        resultados['fecha_binance'] = datetime.now().isoformat()
        try:
            db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
            log_humano("Reporte Binance guardado.")
        except Exception as e:
            log_humano(f"Error al guardar: {e}")

if __name__ == "__main__":
    ejecutar()
