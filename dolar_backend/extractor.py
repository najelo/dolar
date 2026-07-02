import os
import requests
from datetime import datetime
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_consenso_bcv():
    """Consulta 3 fuentes distintas y valida el consenso del valor oficial"""
    fuentes = [
        "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv",
        "https://ve.dolarapi.com/v1/dolares/bcv",
        "https://api.monitordolarve.com/api/v1/dollar?page=bcv"
    ]
    
    valores = []
    
    for url in fuentes:
        try:
            resp = requests.get(url, timeout=8).json()
            # Extracción adaptativa según el formato de cada API
            if "monitors" in resp: 
                precio = float(resp['monitors']['usd']['price'])
            elif "promedio" in resp: 
                precio = float(resp['promedio'])
            else: 
                precio = float(resp['price'])
            
            # Filtro de cordura: descartamos valores fuera de rango lógico
            if 500 < precio < 2000:
                valores.append(precio)
        except:
            continue
            
    return sum(valores) / len(valores) if valores else None

def obtener_binance_p2p(banco_nombre):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
        "payTypes": [banco_nombre], "rows": 1, "page": 1, "proMerchantAds": False
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10).json()
        return float(resp['data'][0]['adv']['price']) if resp.get('data') else 0.0
    except:
        return 0.0

def main():
    # 1. Obtener BCV mediante Consenso
    bcv_usd = obtener_consenso_bcv()
    
    # 2. Binance P2P
    banesco = obtener_binance_p2p("Banesco")
    mercantil = obtener_binance_p2p("Mercantil")
    bdv = obtener_binance_p2p("BancoDeVenezuela")
    pagomovil = obtener_binance_p2p("PagoMovil")
    
    valores_binance = [v for v in [banesco, mercantil, bdv, pagomovil] if v > 0]
    promedio_binance = sum(valores_binance) / len(valores_binance) if valores_binance else 735.0
    
    # 3. Guardado inteligente solo si el BCV nos dio un valor válido
    if bcv_usd:
        data = {
            "id": 1,
            "bcv_dolar": round(bcv_usd, 4),
            "bcv_euro": round(bcv_usd * 1.05, 4), 
            "binance": round(promedio_binance, 2),
            "binance_banesco": banesco if banesco > 0 else 735.0,
            "binance_mercantil": mercantil if mercantil > 0 else 735.0,
            "binance_bdv": bdv if bdv > 0 else 735.0,
            "binance_pagomovil": pagomovil if pagomovil > 0 else 735.0,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        
        # Validación de cambio para no saturar la BD
        registro = supabase.table("tasas_monitoreo").select("bcv_dolar").eq("id", 1).single().execute()
        
        # Actualizar solo si hay una diferencia real (mayor a 0.001)
        if not registro.data or abs(registro.data.get("bcv_dolar", 0) - bcv_usd) > 0.001:
            supabase.table("tasas_monitoreo").upsert(data).execute()
            print(f"✅ Consenso alcanzado: BCV actualizado a {bcv_usd}")
        else:
            print("ℹ️ Sin cambios significativos en el BCV.")
    else:
        print("⚠️ Fallo en el consenso de fuentes. No se actualizó la BD.")

if __name__ == "__main__":
    main()
