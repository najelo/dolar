import os
import requests
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasas():
    # 1. BCV (usando una API de terceros confiable para BCV)
    try:
        bcv_data = requests.get("https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv", timeout=10).json()
        bcv_dolar = float(bcv_data['monitors']['usd']['price'])
        bcv_euro = float(bcv_data['monitors']['eur']['price'])
    except:
        bcv_dolar, bcv_euro = 0.0, 0.0

    # 2. Binance (usando la API P2P de Binance)
    # Ejemplo para USDT/VES (Pago móvil/Bancos)
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "payTypes": ["BankTransfer"]}
        r = requests.post(url, json=payload, timeout=10).json()
        # Tomamos el precio del primer vendedor
        precio_binance = float(r['data'][0]['adv']['price'])
    except:
        precio_binance = 0.0

    return bcv_dolar, bcv_euro, precio_binance

def ejecutar():
    bcv_d, bcv_e, binance = obtener_tasas()
    fecha = datetime.now().isoformat()
    
    # Subir a Supabase
    supabase.table("tasas_monitoreo").upsert({
        "id": 1,
        "bcv_dolar": bcv_d,
        "bcv_euro": bcv_e,
        "binance": binance,
        "ultima_actualizacion": fecha
    }).execute()
    
    print(f"✅ Tasas actualizadas: BCV {bcv_d}, Binance {binance}")

if __name__ == "__main__":
    ejecutar()
