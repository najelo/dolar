import os
import requests
from bs4 import BeautifulSoup  
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv():
    """Extrae el valor real directamente del HTML del BCV"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get("https://www.bcv.org.ve/", headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'lxml')
        
        dolar_text = soup.find("div", {"id": "dolar"}).find("strong").text
        dolar = float(dolar_text.replace('.', '').replace(',', '.'))
        
        euro_text = soup.find("div", {"id": "euro"}).find("strong").text
        euro = float(euro_text.replace('.', '').replace(',', '.'))
        
        return dolar, euro, True # Retornamos los 3 valores correctamente
    except Exception as e:
        print(f"Error extrayendo BCV directo: {e}")
        return 0, 0, False # Fallo

def obtener_binance_p2p(banco_nombre):
    # Lógica de Binance intacta
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
        "payTypes": [banco_nombre], "rows": 1, "page": 1, "proMerchantAds": False
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15).json()
        if resp.get('data') and len(resp['data']) > 0:
            return float(resp['data'][0]['adv']['price'])
    except:
        pass
    return 0.0

def main():
    # 1. Intentar obtener BCV real
    bcv_usd, bcv_eur, exito_bcv = obtener_tasa_bcv()
    
    # 2. Obtener Binance (Lógica intacta)
    banesco = obtener_binance_p2p("Banesco")
    mercantil = obtener_binance_p2p("Mercantil")
    bdv = obtener_binance_p2p("BancoDeVenezuela")
    pagomovil = obtener_binance_p2p("PagoMovil")
    
    valores = [v for v in [banesco, mercantil, bdv, pagomovil] if v > 0]
    promedio = sum(valores) / len(valores) if valores else 735.0
    
    # 3. Lógica de Protección:
    # Solo actualizamos el BCV si la API respondió correctamente (exito_bcv == True)
    # Si falló, usamos los valores actuales de la base de datos para no sobrescribir con error
    if exito_bcv:
        data = {
            "id": 1,
            "bcv_dolar": bcv_usd,
            "bcv_euro": bcv_eur,
            "binance": round(promedio, 2),
            "binance_banesco": banesco if banesco > 0 else 735.0,
            "binance_mercantil": mercantil if mercantil > 0 else 735.0,
            "binance_bdv": bdv if bdv > 0 else 735.0,
            "binance_pagomovil": pagomovil if pagomovil > 0 else 735.0,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        supabase.table("tasas_monitoreo").upsert(data).execute()
        print(f"✅ Éxito, datos enviados a Supabase: {data}")
    else:
        print("⚠️ La API de BCV falló. No se actualizará la base de datos para no corromper los datos actuales.")

if __name__ == "__main__":
    main()
