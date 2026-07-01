import os
import requests
from datetime import datetime
from supabase import create_client, Client

# Inicializar Supabase
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv():
    """Obtiene las tasas oficiales del BCV"""
    try:
        response = requests.get("https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv", timeout=10).json()
        return float(response['monitors']['usd']['price']), float(response['monitors']['eur']['price'])
    except:
        return 633.36, 723.27  # Valores de respaldo

def obtener_tasa_binance(nombre_banco):
    """Obtiene la tasa de un banco en Binance P2P"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY",
        "payTypes": [nombre_banco]
    }
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        return float(response['data'][0]['adv']['price'])
    except:
        return 0.0

def main():
    # Obtener todas las tasas
    bcv_dolar, bcv_euro = obtener_tasa_bcv()
    banesco = obtener_tasa_binance("Banesco")
    mercantil = obtener_tasa_binance("Mercantil")
    bdv = obtener_tasa_binance("BancoDeVenezuela")
    pagomovil = obtener_tasa_binance("MobileTopup")
    
    binance_promedio = round((banesco + mercantil + bdv + pagomovil) / 4, 2)
    fecha_actual = datetime.now().isoformat()

    # Preparar datos
    datos = {
        "id": 1,
        "bcv_dolar": bcv_dolar,
        "bcv_euro": bcv_euro,
        "binance": binance_promedio,
        "binance_banesco": banesco,
        "binance_mercantil": mercantil,
        "binance_bdv": bdv,
        "binance_pagomovil": pagomovil,
        "ultima_actualizacion": fecha_actual
    }

    # Actualizar Supabase
    try:
        supabase.table("tasas_monitoreo").upsert(datos).execute()
        print(f"✅ Sincronización Exitosa: {datos}")
    except Exception as e:
        print(f"❌ Error al subir a Supabase: {e}")

if __name__ == "__main__":
    main()
