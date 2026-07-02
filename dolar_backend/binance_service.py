import os
import requests
from supabase import create_client

def actualizar_tasas_bancos():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Mapeo: nombre de la columna en tu BD -> etiqueta real en Binance
    bancos_map = {
        "binance_banesco": "Banesco",
        "binance_mercantil": "Mercantil",
        "binance_bdv": "Banco de Venezuela",
        "binance_pagomovil": "Pago Movil", # Sin acento
        "binance_provincial": "Provincial"
    }
    
    updates = {}
    
    for columna, etiqueta in bancos_map.items():
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": "SELL",  # Buscamos precio de venta
            "rows": 1,
            "page": 1,
            "payTypes": [etiqueta] # Filtramos específicamente por el banco
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10).json()
            
            if response.get("data") and len(response["data"]) > 0:
                precio = float(response["data"][0]["adv"]["price"])
                updates[columna] = precio
                print(f"✅ {etiqueta} (Venta): {precio}")
            else:
                print(f"⚠️ Sin datos para {etiqueta}")
                    
        except Exception as e:
            print(f"❌ Error obteniendo {etiqueta}: {e}")
    
    # Actualizar todo en un solo movimiento
    if updates:
        supabase.table("tasas_monitoreo").update(updates).eq("id", 1).execute()
        print("🚀 Base de datos actualizada con los precios de venta bancarios.")

if __name__ == "__main__":
    actualizar_tasas_bancos()
