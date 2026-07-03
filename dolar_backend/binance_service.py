import os
import requests
import random
import time
import logging
from supabase import create_client
from datetime import datetime

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_humano(mensaje):
    logging.info(f"🤖 Bot: {mensaje}")

def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/126.0.0.0",
        "Referer": "https://p2p.binance.com/",
        "Accept": "application/json, text/plain, */*"
    })
    return s

def buscar_mejor_tasa(banco_clave, session):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    precios = []
    
    # Buscamos en varias páginas
    for pagina in [1, 2, 3]: 
        payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 20, "page": pagina}
        try:
            time.sleep(random.uniform(5, 8)) 
            res = session.post(url, json=payload, timeout=15)
            data = res.json().get("data", [])
            
            for a in data:
                adv = a.get("adv", {})
                precio = float(adv.get("price", 0))
                # Extraemos nombres de métodos de pago
                metodos = [m.get("tradeMethodName", "").lower() for m in adv.get("tradeMethods", [])]
                nombres = " ".join(metodos)
                
                # --- DEPURACIÓN ---
                # Esto te dirá qué nombres está viendo el bot para que sepas por qué no coincide
                # log_humano(f"Analizando: {nombres} -> Precio: {precio}") 
                
                if banco_clave.lower() in nombres:
                    precios.append(precio)
        except Exception as e:
            log_humano(f"Error en página {pagina}: {e}")
            continue
            
    return max(precios) if precios else None

def ejecutar():
    log_humano("Iniciando jornada...")
    session = get_session()
    
    # Ajuste de claves para que coincidan mejor con Binance (ej: "pago movil" en lugar de "pago")
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
            log_humano(f"¡Éxito! Encontré {col} a {precio}")
        else:
            log_humano(f"No pude encontrar ninguna oferta para {col}")
            
    if resultados:
        resultados['fecha_binance'] = datetime.now().isoformat()
        try:
            db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
            log_humano("Datos guardados en Supabase.")
        except Exception as e:
            log_humano(f"Error al guardar: {e}")

if __name__ == "__main__":
    ejecutar()
