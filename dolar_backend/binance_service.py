import os
import requests
import random
import time
import logging
from supabase import create_client

# Configuración de log profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def obtener_tasa_flexible(palabra_clave, session):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Lista de User-Agents para evitar bloqueos por huella digital
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Referer": "https://p2p.binance.com/",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "rows": 10,
        "page": 1,
        "payTypes": [] 
    }
    
    try:
        # Pausa aleatoria para simular lectura humana
        time.sleep(random.uniform(2, 5))
        
        response = session.post(url, json=payload, headers=headers, timeout=15)
        data = response.json()
        
        if data and "data" in data and len(data["data"]) > 0:
            for anuncio in data["data"]:
                anuncio_info = anuncio.get("adv", {})
                metodos = anuncio_info.get("tradeMethods", [])
                
                for m in metodos:
                    if palabra_clave.lower() in m.get("tradeMethodName", "").lower():
                        return float(anuncio_info.get("price"))
            
            # Respaldo: primer precio disponible
            return float(data["data"][0]["adv"]["price"])
            
    except Exception as e:
        logging.error(f"Error conectando con Binance para '{palabra_clave}': {e}")
    return None

def actualizar_todo():
    logging.info("Iniciando actualización P2P Binance...")
    session = requests.Session()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    busquedas = {
        "binance_bdv": "Venezuela",
        "binance_pagomovil": "Movil",
        "binance_banesco": "Banesco",
        "binance_mercantil": "Mercantil"
    }
    
    resultados = {}
    for col, clave in busquedas.items():
        precio = obtener_tasa_flexible(clave, session)
        if precio:
            resultados[col] = precio
            logging.info(f"✅ Precio {col} obtenido: {precio}")
        else:
            logging.warning(f"⚠️ No se pudo obtener precio para {col}")
    
    # Subida masiva a Supabase para ahorrar peticiones a la DB
    if resultados:
        try:
            supabase.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
            logging.info("🚀 Base de datos actualizada con éxito.")
        except Exception as e:
            logging.error(f"Error al guardar en Supabase: {e}")

if __name__ == "__main__":
    actualizar_todo()
