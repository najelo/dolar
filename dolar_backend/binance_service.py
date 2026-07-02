import os
import requests
from supabase import create_client

def actualizar_binance():
    # Inicializar cliente
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Lista de bancos tal cual los tienes en tus columnas
    bancos = ["banesco", "mercantil", "provincial", "pagomovil", "bdv"]
    
    for operacion in ["BUY", "SELL"]:
        # Consulta de mercado general (evita bloqueos)
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": operacion,
            "rows": 1,
            "page": 1
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10).json()
            
            if response.get("data") and len(response["data"]) > 0:
                precio = float(response["data"][0]["adv"]["price"])
                
                # Preparamos el diccionario de actualización 
                # Los nombres de las llaves deben coincidir con tus columnas:
                # binance_banesco_buy, binance_banesco_sell, etc.
                updates = {}
                for banco in bancos:
                    columna = f"binance_{banco}_{operacion.lower()}"
                    updates[columna] = precio
                
                supabase.table("tasas_monitoreo").update(updates).eq("id", 1).execute()
                print(f"✅ Precios {operacion} actualizados para todos los bancos: {precio}")
            else:
                print(f"⚠️ Sin datos de mercado para {operacion}")
                    
        except Exception as e:
            print(f"❌ Error en Binance {operacion}: {e}")

if __name__ == "__main__":
    actualizar_binance()
