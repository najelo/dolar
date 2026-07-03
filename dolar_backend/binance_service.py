import os
import requests
import random
import time
import logging
from supabase import create_client

# Configuración básica
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_humano(mensaje, estilo="🤖 Bot:"):
    logging.info(f"{estilo} {mensaje}")

def buscar_mejor_tasa(banco_clave, session, ultima_tasa):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    # User-Agent más realista
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    
    # Quitamos tradeType para obtener más resultados y filtramos nosotros
    payload = {"asset": "USDT", "fiat": "VES", "rows": 100, "page": 1}
    
    try:
        time.sleep(random.uniform(3, 6))
        res = session.post(url, json=payload, headers=headers, timeout=15)
        res_data = res.json()
        
        data = res_data.get("data", [])
        if not data: 
            return None
            
        precios = []
        for a in data:
            adv = a.get("adv", {})
            precio = float(adv.get("price", 0))
            metodos = adv.get("tradeMethods", [])
            
            if not isinstance(metodos, list): continue
            
            # Unimos los nombres en un solo string para buscar
            nombres_metodos = " ".join([m.get("tradeMethodName", "").lower() for m in metodos])
            
            if banco_clave.lower() in nombres_metodos:
                if 50 < precio < 5000: # Rango seguro
                    # Ventana flotante contra precios absurdos
                    if ultima_tasa and (precio > (ultima_tasa * 2.5) or precio < (ultima_tasa * 0.4)):
                        continue 
                    precios.append(precio)
        
        return max(precios) if precios else None
    except Exception as e:
        log_humano(f"Error técnico al consultar {banco_clave}: {e}")
        return None

def ejecutar():
    log_humano(random.choice(["Revisando el mercado...", "Analizando tasas...", "Echándole un ojo al P2P..."]))
    
    session = requests.Session()
    # Asegúrate de que tus variables de entorno estén cargadas
    try:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        ultima_data = db.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        precios_previos = ultima_data[0] if ultima_data else {}
    except Exception as e:
        log_humano(f"No pude conectar a la base de datos: {e}")
        precios_previos = {}

    # Etiquetas más cortas y efectivas
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
            log_humano(f"Encontré {precio} VES en {clave}.")
        else:
            log_humano(f"No vi ofertas claras para {clave}.")

    if resultados:
        try:
            db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
            log_humano("Reporte listo y guardado. ¡Todo al día!")
        except Exception as e:
            log_humano(f"Error al guardar en Supabase: {e}")
    else:
        log_humano("El mercado parece estar en pausa o no hay coincidencias. Seguiré pendiente.")

if __name__ == "__main__":
    ejecutar()
