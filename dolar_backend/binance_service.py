import os
import requests
from supabase import create_client

def obtener_tasa_flexible(palabra_clave):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "rows": 20,
        "page": 1
    }
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        if "data" in response:
            for anuncio in response["data"]:
                for m in anuncio["adv"]["tradeMethods"]:
                    if palabra_clave.lower() in m["tradeMethodName"].lower():
                        return float(anuncio["adv"]["price"])
    except Exception:
        pass
    return None

def actualizar_todo():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Lista de bancos a monitorear (sin provincial)
    busquedas = {
        "binance_bdv": "Venezuela",
        "binance_pagomovil": "Movil",
        "binance_banesco": "Banesco",
        "binance_mercantil": "Mercantil"
    }
    
    for col, clave in busquedas.items():
        precio = obtener_tasa_flexible(clave)
        if precio:
            try:
                supabase.table("tasas_monitoreo").update({col: precio}).eq("id", 1).execute()
                print(f"✅ {col} actualizado a: {precio}")
            except Exception as e:
                print(f"⚠️ Error al guardar en {col}: {e}")
        else:
            print(f"⚠️ No se encontró tasa específica para {col}")

if __name__ == "__main__":
    actualizar_todo()
