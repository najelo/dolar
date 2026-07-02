import os
import requests
from supabase import create_client

def actualizar_binance():
    # 1. Configuración de conexión
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Lista de bancos a monitorear
    bancos = ["Banesco", "Mercantil", "Provincial", "PagoMovil", "BDV"]
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    for banco in bancos:
        # Definimos las dos operaciones: BUY (tú compras USDT) y SELL (tú vendes USDT)
        tipos_operacion = {"buy": "BUY", "sell": "SELL"}
        
        for clave, operacion in tipos_operacion.items():
            payload = {
                "asset": "USDT",
                "fiat": "VES",
                "tradeType": operacion,
                "payTypes": [banco],
                "rows": 1,
                "page": 1
            }
            
            try:
                response = requests.post(url_binance, json=payload, timeout=10)
                data = response.json()
                
                if data['data']:
                    precio = float(data['data'][0]['adv']['price'])
                    
                    # Nombre dinámico de la columna (ej: binance_banesco_buy, binance_banesco_sell)
                    columna = f"binance_{banco.lower()}_{clave}"
                    
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {banco} {clave.upper()}: {precio}")
                
            except Exception as e:
                print(f"❌ Error con {banco} en operacion {clave}: {e}")

if __name__ == "__main__":
    actualizar_binance()
