import os
import requests
from supabase import create_client

def actualizar_binance():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Intentamos obtener el precio general de mercado sin filtrar por banco
    # Esto garantiza que el script siempre tenga datos
    for tipo in ["buy", "sell"]:
        operacion = "BUY" if tipo == "buy" else "SELL"
        payload = {
            "asset": "USDT", 
            "fiat": "VES", 
            "tradeType": operacion, 
            "rows": 1,
            "page": 1
        }
        
        try:
            resp = requests.post(url_binance, json=payload, timeout=15).json()
            
            if resp.get('data'):
                precio = float(resp['data'][0]['adv']['price'])
                
                # Guardamos en una columna general de mercado
                columna = f"binance_general_{tipo}"
                
                supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                print(f"✅ Precio general {tipo.upper()} guardado: {precio}")
            else:
                print(f"❌ No se pudo obtener precio general para {tipo}")
                
        except Exception as e:
            print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    actualizar_binance()
