import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv():
    """Scraping directo al BCV con una estrategia de reintento"""
    url = "https://www.bcv.org.ve/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    
    # Intentamos 3 veces si falla
    for i in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=25, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml') # Usamos lxml
                dolar = float(soup.select_one('#dolar strong').text.strip().replace('.', '').replace(',', '.'))
                euro = float(soup.select_one('#euro strong').text.strip().replace('.', '').replace(',', '.'))
                return dolar, euro
        except Exception as e:
            print(f"Intento {i+1} fallido: {e}")
            continue
    return None, None

def obtener_binance_p2p(banco_nombre):
    # Esta parte se queda EXACTAMENTE igual como me pediste
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
        "payTypes": [banco_nombre], "rows": 1, "page": 1, "proMerchantAds": False
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15).json()
        return float(resp['data'][0]['adv']['price']) if resp.get('data') else 0.0
    except:
        return 0.0

def main():
    bcv_usd, bcv_eur = obtener_tasa_bcv()
    
    if bcv_usd and bcv_usd > 600:
        banesco = obtener_binance_p2p("Banesco")
        mercantil = obtener_binance_p2p("Mercantil")
        bdv = obtener_binance_p2p("BancoDeVenezuela")
        pagomovil = obtener_binance_p2p("PagoMovil")
        
        valores = [v for v in [banesco, mercantil, bdv, pagomovil] if v > 0]
        promedio = sum(valores) / len(valores) if valores else 735.0
        
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
        print(f"✅ Éxito: BCV actualizado a {bcv_usd}")
    else:
        print("⚠️ No se pudo conectar al BCV después de varios intentos.")

if __name__ == "__main__":
    main()
