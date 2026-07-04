import os
import requests
import random
import time
import logging
from supabase import create_client
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - 🤖 %(message)s')

def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/126.0.0.0",
        "Referer": "https://p2p.binance.com/",
        "Accept": "application/json, text/plain, */*"
    })
    return s

def buscar_mejor_tasa(banco_nombre, banco_clave, session):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 20, "page": 1}
    try:
        logging.info(f"Escaneando ofertas para: {banco_nombre}...")
        res = session.post(url, json=payload, timeout=15)
        data = res.json().get("data", [])
        precios = [float(a.get("adv", {}).get("price", 0)) for a in data 
                   if any(banco_clave in m.get("tradeMethodName", "").lower() 
                   for m in a.get("adv", {}).get("tradeMethods", []))]
        
        if precios:
            mejor_precio = max(precios)
            logging.info(f"✅ Encontrado: {banco_nombre} a {mejor_precio}")
            return mejor_precio
        return None
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def ejecutar():
    logging.info("--- INICIANDO JORNADA BINANCE ---")
    session = get_session()
    bancos_a_buscar = [
        ("BDV", "venezuela", "binance_bdv"),
        ("PagoMóvil", "pago", "binance_pagomovil"),
        ("Banesco", "banesco", "binance_banesco"),
        ("Mercantil", "mercantil", "binance_mercantil")
    ]
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    ahora = datetime.now().isoformat()
    
    for nombre, clave, columna_db in bancos_a_buscar:
        precio = buscar_mejor_tasa(nombre, clave, session)
        if precio:
            try:
                # 1. Insertar en historial (usando solo los campos correctos)
                supabase.table("historial_tasas").insert({
                    "banco": nombre,
                    "valor": precio,
                    "fecha_registro": ahora
                }).execute()
                logging.info(f"💾 Guardado en Historial: {nombre}")
                
                # 2. Actualizar tabla principal (incluyendo fecha_binance)
                supabase.table("tasas_monitoreo").update({
                    columna_db: precio,
                    "fecha_binance": ahora
                }).eq("id", 1).execute()
                logging.info(f"🔄 Actualizado en tabla principal: {columna_db}")
                
            except Exception as e:
                logging.error(f"❌ Error en Supabase: {e}")
        time.sleep(random.uniform(3, 6))
    logging.info("--- PROCESO BINANCE FINALIZADO ---")

if __name__ == "__main__":
    ejecutar()
