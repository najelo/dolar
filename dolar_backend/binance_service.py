import os
import requests
from supabase import create_client

def actualizar_binance():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Nombres exactos aceptados por la API de Binance (PayTypes)
    bancos_config = {
        "Banesco": "Banesco",
        "Mercantil": "Mercantil",
        "Provincial": "Provincial",
        "PagoMovil": "Pago Movil", # Ajustado
        "BDV": "BDV"
    }
    
    url_binance = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    for nombre_interno, nombre_api in bancos_config.items():
        for tipo in ["buy", "sell"]:
            operacion = "BUY" if tipo == "buy" else "SELL"
            payload = {
                "asset": "USDT", 
                "fiat": "VES", 
                "tradeType": operacion, 
                "payTypes": [nombre_api], 
                "rows": 1
            }
            
            try:
                resp = requests.post(url_binance, json=payload, timeout=15).json()
                
                # Validación clave: Verificamos si 'data' existe y no está vacío
                if resp.get('data') and len(resp['data']) > 0:
                    precio = float(resp['data'][0]['adv']['price'])
                    columna = f"binance_{nombre_interno.lower()}_{tipo}"
                    
                    supabase.table("tasas_monitoreo").update({columna: precio}).eq("id", 1).execute()
                    print(f"✅ {nombre_interno} {tipo.upper()} guardado: {precio}")
                else:
                    print(f"⚠️ Sin anuncios para {nombre_interno} {tipo.upper()}")
                
            except Exception as e:
                print(f"❌ Error con {nombre_interno} {tipo}: {e}")

if __name__ == "__main__":
    actualizar_binance()
