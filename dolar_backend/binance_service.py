import os
import requests
from supabase import create_client

def actualizar_binance():
    # Inicializar cliente
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Lista de bancos según tu tabla
    bancos = ["banesco", "mercantil", "provincial", "pagomovil", "bdv"]
    
    for operacion in ["BUY", "SELL"]:
        # Payload sin filtros específicos de banco para evitar bloqueos
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
                
                # Preparamos el diccionario de actualización para todas las columnas de una vez
                updates = {}
                for banco in bancos:
                    columna = f"binance_{banco}_{operacion.lower()}"
                    updates[columna] = precio
                
                # Una sola petición a la base de datos
                supabase.table("tasas_monitoreo").update(updates).eq("id", 1).execute()
                print(f"✅ Precio {operacion} general capturado y distribuido: {precio}")
            else:
                print(f"⚠️ Sin datos de mercado para {operacion}")
                    
        except Exception as e:
            print(f"❌ Error en Binance {operacion}: {e}")

if __name__ == "__main__":
    actualizar_binance()
