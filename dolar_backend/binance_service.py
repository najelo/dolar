import os
import requests
from supabase import create_client

def actualizar_binance():
    # Inicializar cliente
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Lista de bancos según tus columnas principales
    bancos = ["banesco", "mercantil", "provincial", "pagomovil", "bdv"]
    
    # Usamos tradeType "SELL" (es el precio de venta de USDT, el más usado como referencia)
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "rows": 1,
        "page": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        
        if response.get("data") and len(response["data"]) > 0:
            precio = float(response["data"][0]["adv"]["price"])
            
            # Preparamos el diccionario para actualizar las columnas simples (ej: binance_banesco)
            updates = {}
            for banco in bancos:
                # Ajustamos al nombre de columna que tienes en tu esquema (ej: binance_banesco)
                columna = f"binance_{banco}"
                updates[columna] = precio
            
            # Actualizamos también la columna general 'binance' si existe
            updates["binance"] = precio
            
            supabase.table("tasas_monitoreo").update(updates).eq("id", 1).execute()
            print(f"✅ Precios actualizados para todos los bancos: {precio}")
        else:
            print("⚠️ Sin datos de mercado para actualizar")
                    
    except Exception as e:
        print(f"❌ Error al actualizar Binance: {e}")

if __name__ == "__main__":
    actualizar_binance()
