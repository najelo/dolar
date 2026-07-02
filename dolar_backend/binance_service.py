import os
import requests
from supabase import create_client

def obtener_tasa_segura(palabra_clave):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {"asset": "USDT", "fiat": "VES", "tradeType": "SELL", "rows": 50, "page": 1}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15).json()
        
        # Validación estricta de la estructura de la respuesta
        if response and "data" in response and isinstance(response["data"], list):
            # 1. Intentar buscar por palabra clave
            for anuncio in response["data"]:
                # Revisar tradeMethods
                for m in anuncio.get("adv", {}).get("tradeMethods", []):
                    if palabra_clave.lower() in m.get("tradeMethodName", "").lower():
                        return float(anuncio["adv"]["price"])
                # Revisar título
                if palabra_clave.lower() in anuncio.get("adv", {}).get("advTitle", "").lower():
                    return float(anuncio["adv"]["price"])
            
            # 2. Si no encuentra por palabra, devolver el primer precio disponible (Respaldo)
            return float(response["data"][0]["adv"]["price"])
            
    except Exception as e:
        print(f"Error técnico: {e}")
    return None

def actualizar_todo():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    busquedas = {
        "binance_bdv": "Venezuela",
        "binance_pagomovil": "Movil",
        "binance_banesco": "Banesco",
        "binance_mercantil": "Mercantil",
        "binance_provincial": "Provincial"
    }
    
    for col, clave in busquedas.items():
        precio = obtener_tasa_flexible(clave)
        if precio:
            try:
                # Intentamos actualizar, si falla, atrapamos el error y seguimos
                supabase.table("tasas_monitoreo").update({col: precio}).eq("id", 1).execute()
                print(f"✅ {col} actualizado a: {precio}")
            except Exception as e:
                print(f"⚠️ Error al guardar en columna {col} (Supabase la rechaza): {e}")
        else:
            print(f"⚠️ No se encontró tasa específica para {col}")

if __name__ == "__main__":
    actualizar_todo()
