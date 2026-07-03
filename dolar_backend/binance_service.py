import os
import requests
import random
import time
import logging
from supabase import create_client

# Configuración: Ahora el bot nos habla en español y con detalle
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_humano(mensaje):
    """Función para que el bot se reporte contigo."""
    logging.info(f"🤖 Bot: {mensaje}")

def buscar_mejor_tasa(banco_clave, session):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Payload para venta (Tú vendes USDT)
    payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 20, "page": 1}
    
    try:
        # Simulamos pausas humanas variables
        time.sleep(random.uniform(4, 9))
        res = session.post(url, json=payload, headers=headers, timeout=10).json()
        
        precios = [float(a["adv"]["price"]) for a in res.get("data", []) 
                   if any(banco_clave.lower() in m["tradeMethodName"].lower() for m in a["adv"]["tradeMethods"])
                   and 10 < float(a["adv"]["price"]) < 600]
        
        return max(precios) if precios else None
    except Exception as e:
        log_humano(f"Tuve un pequeño problema técnico al revisar {banco_clave}: {e}")
        return None

def ejecutar():
    log_humano("Iniciando mi rutina de monitoreo...")
    session = requests.Session()
    db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    bancos = {"binance_bdv": "Venezuela", "binance_pagomovil": "Movil", "binance_banesco": "Banesco", "binance_mercantil": "Mercantil"}
    
    resultados = {}
    for col, clave in bancos.items():
        precio = buscar_mejor_tasa(clave, session)
        if precio:
            resultados[col] = precio
            log_humano(f"He encontrado una buena tasa en {col}: {precio} VES.")
        else:
            log_humano(f"No logré encontrar ofertas activas para {col} en este momento.")

    if resultados:
        db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
        log_humano("He terminado mi reporte y actualizado la base de datos. ¡Todo listo!")
    else:
        log_humano("No pude actualizar nada, el mercado parece estar quieto.")

if __name__ == "__main__":
    ejecutar()
