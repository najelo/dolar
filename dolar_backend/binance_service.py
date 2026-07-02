import os
import requests
from supabase import create_client

def actualizar_binance():
    # Inicialización de Supabase
    url_supabase = os.getenv("SUPABASE_URL")
    key_supabase = os.getenv("SUPABASE_KEY")
    if not url_supabase or not key_supabase:
        print("❌ Error: Faltan credenciales de Supabase")
        return
        
    supabase = create_client(url_supabase, key_supabase)
    
    # Mapeo de bancos
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
            
            # Intento 1: Con filtro de banco
            payload = {
                "asset": "USDT", "fiat": "VES", "tradeType": operacion, 
                "payTypes": [codigo_api], "rows": 1, "page": 1
            }
            
            try:
                resp = requests.post(url_binance, json=payload, timeout=10).json()
                
                # Intento 2: Si falla el filtro, intentar búsqueda general
                if not resp.get('data'):
                    print(f"⚠️ Filtro falló para {nombre_bd}, buscando general...")
                    payload_general = {"asset": "USDT", "fiat": "VES", "tradeType": operacion, "rows": 1}
                    resp = requests.post(url_binance, json=payload_general, timeout=10).json()

            if resp.get('data'):
                    precio = float(resp['data'][0]['adv']['price'])
                    columna = f"binance_{nombre_bd}_{tipo}"
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {nombre_bd.upper()} {tipo.upper()} actualizado a: {precio}")
                else:
                    # PLAN B: Si no hay nada, intentamos copiar el de Banesco o dejar un 0.0
                    print(f"⚠️ No hay anuncios para {nombre_bd}. Asignando valor por defecto.")
                    columna = f"binance_{nombre_bd}_{tipo}"
                    # Guardamos un 0.0 o un valor de respaldo para que la app no falle
                    supabase.table("tasas_monitoreo").update({columna: 0.0}).eq("id", 1).execute()
                
            except Exception as e:
                print(f"❌ Error con {nombre_bd} {tipo}: {e}")

if __name__ == "__main__":
    actualizar_binance()
