import os
import requests
import random
import time
import logging
from supabase import create_client
from datetime import datetime

# Configuración de logs con formato profesional
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
        
        precios = []
        for a in data:
            adv = a.get("adv", {})
            metodos = [m.get("tradeMethodName", "").lower() for m in adv.get("tradeMethods", [])]
            
            if any(banco_clave in m for m in metodos):
                precios.append(float(adv.get("price", 0)))
        
        if precios:
            mejor_precio = max(precios)
            logging.info(f"✅ Encontrado: {banco_nombre} a {mejor_precio}")
            return mejor_precio
            
        logging.warning(f"⚠️ No hay ofertas activas para {banco_nombre}")
        return None
        
    except Exception as e:
        logging.error(f"Error conectando con Binance para {banco_nombre}: {e}")
        return None

def ejecutar():
    logging.info("--- INICIANDO JORNADA BINANCE ---")
    session = get_session()
    
    # Nombre, clave de búsqueda, y nombre exacto de la columna en Supabase
    bancos_a_buscar = [
        ("BDV", "venezuela", "binance_bdv"),
        ("PagoMóvil", "pago", "binance_pagomovil"),
        ("Banesco", "banesco", "binance_banesco"),
        ("Mercantil", "mercantil", "binance_mercantil")
    ]
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    for nombre, clave, columna_db in bancos_a_buscar:
        precio = buscar_mejor_tasa(nombre, clave, session)
        
        if precio:
            # 1. Guardar en historial
            payload_historial = {
                "banco": nombre,
                "valor": precio,
                "fecha_registro": datetime.now().isoformat()
            }
            try:
                supabase.table("historial_tasas").insert(payload_historial).execute()
                logging.info(f"💾 Guardado en Historial: {nombre}")
                
                # 2. Actualizar tabla de monitoreo (fila con ID 1)
                supabase.table("tasas_monitoreo").update({columna_db: precio}).eq("id", 1).execute()
                logging.info(f"🔄 Actualizado en tabla principal: {columna_db} = {precio}")
                
            except Exception as e:
                logging.error(f"❌ Error guardando en Supabase: {e}")
        
        time.sleep(random.uniform(3, 6))

    logging.info("--- PROCESO BINANCE FINALIZADO ---")

if __name__ == "__main__":
    ejecutar()
