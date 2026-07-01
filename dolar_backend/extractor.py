import os
import requests
import urllib3
import re
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Desactivar advertencias SSL para el BCV debido a problemas de certificados locales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def obtener_tasa_bcv(moneda):
    url = "http://www.bcv.org.ve/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        selector = '#dolar > div.field-content' if moneda == "dolar" else '#euro > div.field-content'
        texto = soup.select_one(selector).text.strip()
        
        # Limpieza: Extrae solo números, puntos y comas, luego convierte la coma decimal a punto
        numero_limpio = re.sub(r'[^0-9,.]', '', texto).replace(',', '.')
        
        return float(numero_limpio)
    except Exception as e:
        print(f"Error BCV ({moneda}): {e}")
        return 0.0

def obtener_tasa_binance():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        data = {
            "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
            "page": 1, "rows": 1, "payTypes": ["MobileTopup"]
        }
        response = requests.post(url, json=data, timeout=10).json()
        
        # --- LÍNEA DE DEBUG ---
        print(f"DEBUG RESPUESTA BINANCE: {response}") 
        # ----------------------
        
        if 'data' in response and len(response['data']) > 0:
            return float(response['data'][0]['adv']['price'])
        return 0.0
    except Exception as e:
        print(f"Error Binance detallado: {e}")
        return 0.0

def ejecutar_actualizacion():
    tasa_dolar = obtener_tasa_bcv("dolar")
    tasa_euro = obtener_tasa_bcv("euro")
    tasa_binance = obtener_tasa_binance()

    if tasa_dolar == 0:
        print("No se pudo obtener la tasa del BCV, abortando.")
        return

    # Actualizar tabla principal
    supabase.table("tasas_monitoreo").upsert({
        "id": 1,
        "bcv_dolar": tasa_dolar,
        "bcv_euro": tasa_euro,
        "binance": tasa_binance
    }).execute()

    # Insertar en historial
    fecha = datetime.now().isoformat()
    datos_historial = [
        {"banco": "BCV Dólar", "valor": tasa_dolar, "fecha": fecha},
        {"banco": "BCV Euro", "valor": tasa_euro, "fecha": fecha},
        {"banco": "BINANCE", "valor": tasa_binance, "fecha": fecha}
    ]
    supabase.table("historial_tasas").insert(datos_historial).execute()
    
    print(f"✅ Sincronizado correctamente: Dolar {tasa_dolar}, Euro {tasa_euro}, Binance {tasa_binance}")

if __name__ == "__main__":
    ejecutar_actualizacion()
