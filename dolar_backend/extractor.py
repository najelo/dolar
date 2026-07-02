import os
import requests
import time
from bs4 import BeautifulSoup  
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv():
    """Extrae con reintentos para dar tiempo al servidor del BCV."""
    intentos = 3
    for i in range(intentos):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            response = requests.get("https://www.bcv.org.ve/", headers=headers, timeout=25, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            dolar_tag = soup.select_one('#dolar strong')
            euro_tag = soup.select_one('#euro strong')
            
            if dolar_tag and euro_tag:
                dolar = float(dolar_tag.text.strip().replace('.', '').replace(',', '.'))
                euro = float(euro_tag.text.strip().replace('.', '').replace(',', '.'))
                return dolar, euro, True
            
            print(f"⚠️ Intento {i+1} fallido: Contenido no encontrado.")
        except Exception as e:
            print(f"⚠️ Intento {i+1} fallido: {e}")
        
        if i < intentos - 1:
            time.sleep(10) # Espera 10 segundos antes de reintentar
            
    return None, None, False

def obtener_binance_p2p(banco_nombre):
    # Tu lógica de Binance se mantiene intacta
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
    # 1. Obtener datos
    bcv_usd, bcv_eur, exito_bcv = obtener_tasa_bcv()
    banesco = obtener_binance_p2p("Banesco")
    mercantil = obtener_binance_p2p("Mercantil")
    bdv = obtener_binance_p2p("BancoDeVenezuela")
    pagomovil = obtener_binance_p2p("PagoMovil")
    
    valores = [v for v in [banesco, mercantil, bdv, pagomovil] if v > 0]
    promedio = sum(valores) / len(valores) if valores else 735.0
    
    # 2. Actualización a Supabase
    # Si el BCV falla (exito_bcv=False), solo actualizamos Binance para no perder esa info
    if exito_bcv and bcv_usd > 600:
        data = {
            "bcv_dolar": bcv_usd,
            "bcv_euro": bcv_eur,
            "binance": round(promedio, 2),
            "binance_banesco": banesco if banesco > 0 else 735.0,
            "binance_mercantil": mercantil if mercantil > 0 else 735.0,
            "binance_bdv": bdv if bdv > 0 else 735.0,
            "binance_pagomovil": pagomovil if pagomovil > 0 else 735.0,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        supabase.table("tasas_monitoreo").update(data).eq("id", 1).execute()
        print(f"✅ Éxito: Base de datos actualizada con BCV {bcv_usd}")
    else:
        # Si BCV falla, solo actualizamos Binance
        data_binance = {
            "binance": round(promedio, 2),
            "binance_banesco": banesco if banesco > 0 else 735.0,
            "binance_mercantil": mercantil if mercantil > 0 else 735.0,
            "binance_bdv": bdv if bdv > 0 else 735.0,
            "binance_pagomovil": pagomovil if pagomovil > 0 else 735.0
        }
        supabase.table("tasas_monitoreo").update(data_binance).eq("id", 1).execute()
        print("ℹ️ BCV no disponible. Solo se actualizaron tasas de Binance.")

if __name__ == "__main__":
    main()
