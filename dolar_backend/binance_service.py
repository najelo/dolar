import os
import requests
import random
import time
import logging
from supabase import create_client

# Configuración de logs con formato amigable
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_humano(mensaje, estilo="🤖 Bot:"):
    logging.info(f"{estilo} {mensaje}")

def buscar_mejor_tasa(banco_clave, session, ultima_tasa):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    # Solicitamos 50 filas para asegurar cobertura
    payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "rows": 50, "page": 1}
    
    try:
        time.sleep(random.uniform(4, 8))
        res = session.post(url, json=payload, headers=headers, timeout=10)
        data = res.json().get("data")
        
        if data is None: return None
            
        precios = []
        for a in data:
            adv = a.get("adv", {})
            precio = float(adv.get("price", 0))
            metodos = adv.get("tradeMethods", [])
            
            if not isinstance(metodos, list): continue
            
            # Filtro inteligente de palabras clave
            nombres = [m.get("tradeMethodName", "").lower() for m in metodos]
            if banco_clave.lower() in str(nombres):
                # Ventana flotante: solo descartamos si es una locura estadística
                if precio > 50:
                    if ultima_tasa and (precio > (ultima_tasa * 3) or precio < (ultima_tasa * 0.5)):
                        continue 
                    precios.append(precio)
        
        return max(precios) if precios else None
    except:
        return None

def ejecutar():
    frases_inicio = ["Echándole un ojo al mercado...", "Revisando qué tal se mueve el P2P...", "Iniciando mi rutina de monitoreo..."]
    log_humano(random.choice(frases_inicio))
    
    session = requests.Session()
    try:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        ultima_data = db.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        precios_previos = ultima_data[0] if ultima_data else {}
    except:
        precios_previos = {}

    bancos = {
        "binance_bdv": "Venezuela", 
        "binance_pagomovil": "Pago Movil", 
        "binance_banesco": "Banesco", 
        "binance_mercantil": "Mercantil"
    }
    
    resultados = {}
    for col, clave in bancos.items():
        precio = buscar_mejor_tasa(clave, session, precios_previos.get(col))
        if precio:
            resultados[col] = precio
            log_humano(f"Encontré una buena tasa en {clave}: {precio} VES.")
        else:
            log_humano(f"No logré encontrar ofertas válidas para {clave} ahora mismo.")

    if resultados:
        db.table("tasas_monitoreo").update(resultados).eq("id", 1).execute()
        # Comentario humano según el resultado
        promedio = sum(resultados.values()) / len(resultados)
        opinion = "El mercado está movido." if promedio > 800 else "Todo se ve tranquilo por hoy."
        log_humano(f"He terminado mi reporte. {opinion} ¡Ya está todo guardado en la base de datos!")
    else:
        log_humano("El mercado parece estar un poco dormido. No pude actualizar nada esta vez.")

if __name__ == "__main__":
    ejecutar()
