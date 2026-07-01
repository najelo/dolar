import os
import requests
from datetime import datetime
from supabase import create_client, Client

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_datos_bcv():
    """Obtiene datos de BCV de una fuente confiable"""
    try:
        # API alternativa más estable
        res = requests.get("https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv", timeout=15).json()
        return float(res['monitors']['usd']['price']), float(res['monitors']['eur']['price'])
    except:
        return 633.36, 723.27

def obtener_binance_p2p(banco_nombre):
    """Extrae precio real de Binance P2P"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json'}
    # Nota: Binance requiere un payload específico
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
        "payTypes": [banco_nombre], "rows": 1
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15).json()
        if 'data' in resp and len(resp['data']) > 0:
            return float(resp['data'][0]['adv']['price'])
        return 0.0
    except:
        return 0.0

def main():
    bcv_usd, bcv_eur = obtener_datos_bcv()
    
    # Mapeo de bancos (usando nombres estándar P2P)
    bancos = {
        "Banesco": "Banesco",
        "Mercantil": "Mercantil",
        "BDV": "BancoDeVenezuela",
        "PagoMóvil": "PagoMovil" # Cambiado a PagoMovil estándar
    }
    
    tasas = {k: obtener_binance_p2p(v) for k, v in bancos.items()}
    
    # Si alguna tasa Binance es 0, usamos el valor BCV como base para no tener errores
    promedio_binance = sum(t for t in tasas.values() if t > 0) / len([t for t in tasas.values() if t > 0])
    
    data = {
        "id": 1,
        "bcv_dolar": bcv_usd,
        "bcv_euro": bcv_eur,
        "binance": round(promedio_binance, 2),
        "binance_banesco": tasas["Banesco"] if tasas["Banesco"] > 0 else bcv_usd,
        "binance_mercantil": tasas["Mercantil"] if tasas["Mercantil"] > 0 else bcv_usd,
        "binance_bdv": tasas["BDV"] if tasas["BDV"] > 0 else bcv_usd,
        "binance_pagomovil": tasas["PagoMóvil"] if tasas["PagoMóvil"] > 0 else bcv_usd,
        "ultima_actualizacion": datetime.now().isoformat()
    }

    try:
        supabase.table("tasas_monitoreo").upsert(data).execute()
        print(f"✅ Sincronización exitosa: {data}")
    except Exception as e:
        print(f"❌ Error crítico en Supabase: {e}")

if __name__ == "__main__":
    main()
