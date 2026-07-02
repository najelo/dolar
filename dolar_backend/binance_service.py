import os
import requests
from supabase import create_client

def actualizar_binance():
    # Inicializar cliente
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # URL de API P2P (Punto final estable)
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Mapeo de bancos
    bancos = {
        "banesco": "Banesco",
        "mercantil": "Mercantil",
        "provincial": "Provincial",
        "pagomovil": "Pago Móvil",
        "bdv": "Banco de Venezuela"
    }

    for nombre, etiqueta in bancos.items():
        for operacion in ["BUY", "SELL"]:
            # Usamos una estructura de payload más genérica que es aceptada siempre
            payload = {
                "asset": "USDT",
                "fiat": "VES",
                "tradeType": operacion,
                "rows": 1,
                "payTypes": [etiqueta]
            }
            
            try:
                response = requests.post(url, json=payload, timeout=10).json()
                
                # Verificamos si hay datos
                if response.get("data") and len(response["data"]) > 0:
                    precio = float(response["data"][0]["adv"]["price"])
                    columna = f"binance_{nombre}_{operacion.lower()}"
                    
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {nombre.upper()} {operacion}: {precio}")
                else:
                    print(f"⚠️ Sin resultados para {nombre} {operacion}")
                    
            except Exception as e:
                print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    actualizar_binance()
