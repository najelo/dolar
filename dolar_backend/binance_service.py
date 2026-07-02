import os
import requests
from supabase import create_client

def actualizar_binance():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Mapeo: nombre_interno_en_tabla : código_que_espera_la_API_de_Binance
    bancos_map = {
        "banesco": "Banesco",
        "mercantil": "Mercantil",
        "provincial": "Provincial",
        "pagomovil": "Pago Movil", 
        "bdv": "BDV"
    }
    
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    for nombre_bd, codigo_api in bancos_map.items():
        for tipo in ["buy", "sell"]:
            operacion = "BUY" if tipo == "buy" else "SELL"
            payload = {
                "asset": "USDT", "fiat": "VES", "tradeType": operacion, 
                "payTypes": [codigo_api], "rows": 1, "page": 1
            }
            
            try:
                resp = requests.post(url_binance, json=payload, timeout=10).json()
                
                if resp.get('data') and len(resp['data']) > 0:
                    precio = float(resp['data'][0]['adv']['price'])
                    columna = f"binance_{nombre_bd}_{tipo}"
                    
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {nombre_bd.upper()} {tipo.upper()} actualizado a: {precio}")
                else:
                    print(f"⚠️ No hay anuncios activos para {nombre_bd} ({tipo.upper()})")
                
            except Exception as e:
                print(f"❌ Error con {nombre_bd}: {e}")

if __name__ == "__main__":
    actualizar_binance()
