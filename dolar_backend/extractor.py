import os
import requests
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_banco(nombre_banco_p2p):
    """Obtiene la tasa de un banco específico en Binance P2P"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY",
        "payTypes": [nombre_banco_p2p] 
    }
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        # Tomamos el precio del primer anuncio disponible
        return float(response['data'][0]['adv']['price'])
    except:
        return 0.0

def main():
    # Mapeo de bancos (el nombre debe coincidir con como Binance los identifica)
    tasas = {
        "Banesco": obtener_tasa_banco("Banesco"),
        "Mercantil": obtener_tasa_banco("Mercantil"),
        "BDV": obtener_tasa_banco("BancoDeVenezuela"),
        "PagoMóvil": obtener_tasa_banco("MobileTopup") # O el identificador correcto
    }
    
    fecha_actual = datetime.now().isoformat()

    # Subir a Supabase
    supabase.table("tasas_monitoreo").upsert({
        "id": 1,
        "binance_banesco": tasas["Banesco"],
        "binance_mercantil": tasas["Mercantil"],
        "binance_bdv": tasas["BDV"],
        "binance_pagomovil": tasas["PagoMóvil"],
        "ultima_actualizacion": fecha_actual
    }).execute()

    print(f"✅ Tasas extraídas: {tasas}")

if __name__ == "__main__":
    main()
