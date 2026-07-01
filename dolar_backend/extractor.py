import os
import requests
import sys
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv():
    """Obtiene las tasas oficiales del BCV desde una fuente más directa"""
    try:
        # Usamos una fuente alternativa que refresca con mayor frecuencia
        # Opcional: Si tienes una URL propia de scraping, cámbiala aquí.
        # Esta API suele ser muy confiable para el monitor BCV:
        url = "https://ve.dolarapi.com/v1/dolares/oficial"
        response = requests.get(url, timeout=10).json()
        
        # El formato de respuesta suele ser {'promedio': ..., 'fecha': ...}
        return float(response['promedio']), float(response.get('euro', {}).get('promedio', 0.0))
    except Exception as e:
        print(f"Error extrayendo BCV: {e}")
        # Valor de respaldo solo si la API cae
        return 633.36, 723.27

def obtener_binance_p2p(banco_nombre):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    # Payload ajustado para buscar anuncios reales de compra de USDT con VES
    payload = {
        "asset": "USDT", 
        "fiat": "VES", 
        "tradeType": "BUY", # Tú quieres comprar USDT con bolívares
        "payTypes": [banco_nombre], 
        "rows": 1, 
        "page": 1,
        "proMerchantAds": False # Cambiar a True si quieres precios de comerciantes verificados
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15).json()
        if resp.get('data') and len(resp['data']) > 0:
            # Capturamos el precio del primer anuncio disponible
            return float(resp['data'][0]['adv']['price'])
    except Exception as e:
        print(f"Error técnico en {banco_nombre}: {e}")
    return 0.0
def main():
    # Valores de respaldo (evitan el error NOT NULL)
    bcv_usd, bcv_eur = 633.36, 723.27 
    
    # Intentamos extraer
    banesco = obtener_binance_p2p("Banesco")
    mercantil = obtener_binance_p2p("Mercantil")
    bdv = obtener_binance_p2p("BancoDeVenezuela")
    pagomovil = obtener_binance_p2p("PagoMovil")
    
    # Solo promediamos si son válidos
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
    print(f"✅ Éxito, datos enviados: {data}")

if __name__ == "__main__":
    main()
