import os
import requests
from supabase import create_client

def actualizar_binance():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Mapeo exacto basado en la interfaz de Binance que enviaste
    bancos_map = {
        "banesco": "Banesco",
        "mercantil": "Mercantil",
        "provincial": "Provincial",
        "pagomovil": "Pago Móvil",
        "bdv": "Banco de Venezuela"
    }
    
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    for nombre_bd, codigo_api in bancos_map.items():
        for tipo in ["buy", "sell"]:
            operacion = "BUY" if tipo == "buy" else "SELL"
            payload = {
                "asset": "USDT", "fiat": "VES", "tradeType": operacion, 
                "payTypes": [codigo_api], "rows": 1
            }
            
            try:
                resp = requests.post(url_binance, json=payload, timeout=10).json()
                
                if resp.get('data') and len(resp['data']) > 0:
                    precio = float(resp['data'][0]['adv']['price'])
                    columna = f"binance_{nombre_bd}_{tipo}"
                    
                    # Actualizamos la columna específica
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {nombre_bd.upper()} {tipo.upper()}: {precio}")
                else:
                    print(f"⚠️ No hay anuncios para {nombre_bd} ({tipo.upper()})")
                    
            except Exception as e:
                print(f"❌ Error en {nombre_bd} {tipo}: {e}")

if __name__ == "__main__":
    actualizar_binance()
