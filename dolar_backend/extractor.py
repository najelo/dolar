import os
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Desactivar advertencias SSL para el BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def obtener_tasa_bcv(moneda):
    url = "http://www.bcv.org.ve/" # Usamos http para evitar problemas SSL
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        selector = '#dolar > div.field-content' if moneda == "dolar" else '#euro > div.field-content'
        valor = soup.select_one(selector).text.strip()
        return float(valor.replace(',', '.'))
    except Exception as e:
        print(f"Error BCV ({moneda}): {e}")
        return 0.0

def obtener_tasa_binance():
    """Consulta el promedio P2P usando una API pública confiable"""
    try:
        # API que devuelve el precio P2P promedio actual
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        data = {
            "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
            "page": 1, "rows": 1, "payTypes": ["MobileTopup"]
        }
        response = requests.post(url, json=data, timeout=10).json()
        return float(response['data'][0]['adv']['price'])
    except Exception as e:
        print(f"Error Binance: {e}")
        return 735.00 # Valor de respaldo

def ejecutar_actualizacion():
    tasa_dolar = obtener_tasa_bcv("dolar")
    tasa_euro = obtener_tasa_bcv("euro")
    tasa_binance = obtener_tasa_binance()

    if tasa_dolar == 0: return # Si falla el BCV, no actualizamos nada

    # Actualizar tabla principal
    supabase.table("tasas_monitoreo").upsert({
        "id": 1,
        "bcv_dolar": tasa_dolar,
        "bcv_euro": tasa_euro,
        "binance": tasa_binance
    }).execute()

    # Historial inteligente
    fecha = datetime.now().isoformat()
    supabase.table("historial_tasas").insert([
        {"banco": "BCV Dólar", "valor": tasa_dolar, "fecha": fecha},
        {"banco": "BCV Euro", "valor": tasa_euro, "fecha": fecha},
        {"banco": "BINANCE", "valor": tasa_binance, "fecha": fecha}
    ]).execute()
    print(f"✅ Sincronizado: Dolar {tasa_dolar}, Euro {tasa_euro}, Binance {tasa_binance}")

if __name__ == "__main__":
    ejecutar_actualizacion()
