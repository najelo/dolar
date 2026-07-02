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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        session = requests.Session()
        response = session.get("https://www.bcv.org.ve/", headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        dolar_text = soup.select_one('#dolar strong').text.strip()
        dolar = float(dolar_text.replace('.', '').replace(',', '.'))
        
        euro_text = soup.select_one('#euro strong').text.strip()
        euro = float(euro_text.replace('.', '').replace(',', '.'))
        
        return dolar, euro, True
    except Exception as e:
        print(f"❌ ERROR EN SCRAPING: {e}")
        return 0, 0, False

def obtener_binance_p2p(banco_nombre):
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
    
    # 2. Protección: Solo actualizar si hay éxito y valor coherente
    if exito_bcv and bcv_usd > 600:
        # Consultar valor actual en Supabase para comparar
        try:
            registro = supabase.table("tasas_monitoreo").select("bcv_dolar").eq("id", 1).single().execute()
            valor_db = registro.data.get("bcv_dolar")
        except:
            valor_db = 0

        # Solo hacer upsert si la tasa BCV es diferente a la guardada
        if bcv_usd != valor_db:
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
            print(f"✅ Cambio detectado: Base de datos actualizada a {bcv_usd}")
        else:
            print("ℹ️ Tasa BCV sin cambios. No es necesario actualizar.")
    else:
        print(f"⚠️ BCV falló o valor ilógico ({bcv_usd}). No se hizo nada.")

if __name__ == "__main__":
    main()
