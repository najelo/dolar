import os
import requests
import random
import time
import logging
from supabase import create_client
from datetime import datetime

# Configuración de logs
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
        res = session.post(url, json=payload, timeout=15)
        data = res.json().get("data", [])
        precios = []
        for a in data:
            adv = a.get("adv", {})
            # Manejo seguro para evitar 'NoneType'
            methods = adv.get("tradeMethods") or []
            for m in methods:
                name = m.get("tradeMethodName") or ""
                if banco_clave in name.lower():
                    precios.append(float(adv.get("price", 0)))
        
        return max(precios) if precios else None
    except Exception as e:
        logging.error(f"Error en red/parsing para {banco_nombre}: {e}")
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
            # 1. Intentar guardar en historial (bloque independiente)
            try:
                supabase.table("historial_tasas").insert({
                    "banco": nombre,
                    "valor": precio,
                    "fecha_registro": ahora
                }).execute()
                logging.info(f"💾 Guardado en Historial: {nombre}")
            except Exception as e:
                logging.warning(f"⚠️ Error al insertar en historial (Trigger?): {e}")
            
            # 2. Intentar actualizar tabla principal (bloque independiente)
            # He quitado 'fecha_binance' por si es la causa del error 400
            try:
                supabase.table("tasas_monitoreo").update({
                    columna_db: precio
                }).eq("id", 1).execute()
                logging.info(f"🔄 Actualizado en tabla principal: {nombre}")
            except Exception as e:
                logging.error(f"❌ Error al actualizar tasa en Supabase: {e}")
        
        time.sleep(random.uniform(3, 6))

    logging.info("--- PROCESO BINANCE FINALIZADO ---")

if __name__ == "__main__":
    ejecutar()
