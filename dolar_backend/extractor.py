import os
import requests
import urllib3
import re
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Desactivar advertencias SSL para el BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv(moneda):
    url = "http://www.bcv.org.ve/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        selector = '#dolar > div.field-content' if moneda == "dolar" else '#euro > div.field-content'
        texto = soup.select_one(selector).text.strip()
        return float(re.sub(r'[^0-9,.]', '', texto).replace(',', '.'))
    except Exception as e:
        print(f"Error BCV ({moneda}): {e}")
        return 0.0

def obtener_tasas_binance_detalladas():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        data = {"asset": "USDT", "fiat": "VES", "tradeType": "BUY", "page": 1, "rows": 10, "payTypes": ["ALL"]}
        response = requests.post(url, json=data, timeout=15).json()
        
        # Agregamos 'Binance' (promedio o primera tasa) al diccionario
        tasas = {"Binance": 0.0, "Banesco": 0.0, "Mercantil": 0.0, "BDV": 0.0, "PagoMovil": 0.0}
        
        if 'data' in response:
            # Capturamos la primera tasa general para la columna 'binance'
            if len(response['data']) > 0:
                tasas["Binance"] = float(response['data'][0]['adv']['price'])
            
            # Capturamos las tasas por banco
            for item in response['data']:
                precio = float(item['adv']['price'])
                metodos = [m['tradeMethodName'] for m in item['adv']['tradeMethods']]
                for m in metodos:
                    if "Banesco" in m and tasas["Banesco"] == 0: tasas["Banesco"] = precio
                    if "Mercantil" in m and tasas["Mercantil"] == 0: tasas["Mercantil"] = precio
                    if "Venezuela" in m and tasas["BDV"] == 0: tasas["BDV"] = precio
                    if "Pago Movil" in m and tasas["PagoMovil"] == 0: tasas["PagoMovil"] = precio
        return tasas
    except Exception as e:
        print(f"Error Binance: {e}")
        return {"Binance": 0.0, "Banesco": 0.0, "Mercantil": 0.0, "BDV": 0.0, "PagoMovil": 0.0}

# En tu función ejecutar_actualizacion:
supabase.table("tasas_monitoreo").upsert({
    "id": 1,
    "bcv_dolar": tasa_dolar,
    "bcv_euro": tasa_euro,
    "binance": tasas_b["Binance"],        # <--- Nueva línea
    "binance_banesco": tasas_b["Banesco"],
    "binance_mercantil": tasas_b["Mercantil"],
    "binance_bdv": tasas_b["BDV"],
    "binance_pagomovil": tasas_b["PagoMovil"],
    "ultima_actualizacion": datetime.now().isoformat()
}).execute()

def ejecutar_actualizacion():
    tasa_dolar = obtener_tasa_bcv("dolar")
    tasa_euro = obtener_tasa_bcv("euro")
    tasas_binance = obtener_tasas_binance_detalladas()

    if tasa_dolar == 0:
        print("Error al obtener datos del BCV.")
        return

    # Actualizar tabla principal (Asegúrate de que tu tabla tenga estas columnas)
    supabase.table("tasas_monitoreo").upsert({
        "id": 1,
        "bcv_dolar": tasa_dolar,
        "bcv_euro": tasa_euro,
        "binance_banesco": tasas_binance["Banesco"],
        "binance_mercantil": tasas_binance["Mercantil"],
        "binance_bdv": tasas_binance["BDV"],
        "binance_pagomovil": tasas_binance["PagoMovil"]
    }).execute()

    # Insertar en historial
    fecha = datetime.now().isoformat()
    datos_historial = [
        {"banco": "BCV Dólar", "valor": tasa_dolar, "fecha": fecha},
        {"banco": "BCV Euro", "valor": tasa_euro, "fecha": fecha}
    ]
    # Agregar solo las tasas de Binance que fueron encontradas (>0)
    for banco, valor in tasas_binance.items():
        if valor > 0:
            datos_historial.append({"banco": f"Binance {banco}", "valor": valor, "fecha": fecha})
            
    supabase.table("historial_tasas").insert(datos_historial).execute()
    print(f"✅ Sincronizado: BCV {tasa_dolar}, Binance Banesco {tasas_binance['Banesco']}")

if __name__ == "__main__":
    ejecutar_actualizacion()
