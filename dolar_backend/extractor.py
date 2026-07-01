import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar credenciales
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_tasa_bcv(moneda):
    """Extrae la tasa directamente desde la web del BCV"""
    url = "http://www.bcv.org.ve/"
    try:
        # User-Agent es vital para que no bloqueen la conexión
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Selectores CSS para identificar el precio en la web del BCV
        selector = '#dolar > div.field-content' if moneda == "dolar" else '#euro > div.field-content'
        valor = soup.select_one(selector).text.strip()
        
        return float(valor.replace(',', '.'))
    except Exception as e:
        print(f"Error extrayendo {moneda}: {e}")
        return 0.0

def ejecutar_actualizacion():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción real...")
        
        # Obtenemos los valores reales de la web
        tasa_bcv_dolar = obtener_tasa_bcv("dolar")
        tasa_bcv_euro = obtener_tasa_bcv("euro")
        
        # Tasas Binance (puedes mantener estos fijos o crear otra función de scraping para Binance)
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil) / 2, 2)
        
        # Validar que obtuvimos datos
        if tasa_bcv_dolar == 0 or tasa_bcv_euro == 0:
            print("⚠️ No se pudo obtener datos frescos, manteniendo valores anteriores.")
            return

        # 1. Obtener estado actual en Supabase para comparar
        db_actual = supabase.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        tasa_db = db_actual[0] if db_actual else {}

        # 2. Actualizar tasa actual (Upsert)
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv_dolar": tasa_bcv_dolar,
            "bcv_euro": tasa_bcv_euro,
            "binance": tasa_binance_promedio
        }).execute()

        # 3. Historial inteligente (Insertar solo si cambió)
        if tasa_bcv_euro != tasa_db.get('bcv_euro') or tasa_bcv_dolar != tasa_db.get('bcv_dolar'):
            fecha_actual = datetime.now().isoformat()
            datos_historial = [
                {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
                {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual}
            ]
            supabase.table("historial_tasas").insert(datos_historial).execute()
            print(f"🟩 Valores actualizados a: Dólar {tasa_bcv_dolar}, Euro {tasa_bcv_euro}")
        else:
            print("ℹ️ Sin cambios en BCV. Historial omitido.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    ejecutar_actualizacion()
