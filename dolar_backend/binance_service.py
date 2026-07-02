import os
import requests
from supabase import create_client

def actualizar_tasas_bancos():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    bancos_map = {
        "binance_banesco": "Banesco",
        "binance_mercantil": "Mercantil",
        "binance_bdv": "Banco de Venezuela",
        "binance_pagomovil": "Pago Movil",
        "binance_provincial": "Provincial"
    }
    
    for columna, etiqueta in bancos_map.items():
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": "SELL",
            "rows": 1,
            "page": 1,
            "payTypes": [etiqueta]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10).json()
            
            if response.get("data") and len(response["data"]) > 0:
                precio = float(response["data"][0]["adv"]["price"])
                
                # Actualización individual por columna
                # Si esto falla, el 'try' atrapará el error y el bucle continuará
                supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                print(f"✅ {etiqueta} actualizado: {precio}")
            else:
                print(f"⚠️ Sin datos para {etiqueta}")
                    
        except Exception as e:
            print(f"❌ Error al actualizar {columna}: {e}")

if __name__ == "__main__":
    actualizar_tasas_bancos()
