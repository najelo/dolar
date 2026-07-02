import os
import requests
from supabase import create_client

def actualizar_binance():
    # 1. Configuración
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Lista completa incluyendo BDV
    bancos = ["Banesco", "Mercantil", "Provincial", "PagoMovil", "BDV"]
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    for banco in bancos:
        for tipo in ["buy", "sell"]:
            operacion = "BUY" if tipo == "buy" else "SELL"
            payload = {"asset": "USDT", "fiat": "VES", "tradeType": operacion, "payTypes": [banco], "rows": 1}
            
            try:
                resp = requests.post(url_binance, json=payload, timeout=10).json()
                precio = float(resp['data'][0]['adv']['price'])
                
                # Nombre de columna que debe existir en Supabase: binance_bdv_buy, etc.
                columna = f"binance_{banco.lower()}_{tipo}"
                
                # Actualizar
                supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                print(f"✅ {banco} {tipo.upper()} guardado en {columna}: {precio}")
                
            except Exception as e:
                print(f"❌ Error con {banco} {tipo}: {e}")

if __name__ == "__main__":
    actualizar_binance()
