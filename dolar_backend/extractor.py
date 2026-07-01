import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_tasa_bcv(moneda):
    """Extrae la tasa desde la web del BCV"""
    url = "http://www.bcv.org.ve/"
    try:
        # Usamos un header para parecer un navegador real
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Selectores típicos en el BCV
        if moneda == "dolar":
            valor = soup.select_one('#dolar > div.field-content').text.strip()
        else:
            valor = soup.select_one('#euro > div.field-content').text.strip()
            
        return float(valor.replace(',', '.'))
    except Exception as e:
        print(f"Error extrayendo {moneda}: {e}")
        return 0.0

def ejecutar_actualizacion():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción real...")
        
        # Extraer tasas reales
        tasa_bcv_dolar = obtener_tasa_bcv("dolar")
        tasa_bcv_euro = obtener_tasa_bcv("euro")
        
        # Tasas simuladas (o podrías hacer scraping de Binance también)
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil) / 2, 2)
        
        if tasa_bcv_dolar == 0 or tasa_bcv_euro == 0:
            print("❌ Error: No se pudo obtener datos del BCV. Abortando.")
            return

        # 1. Obtener estado actual en Supabase
        db_actual = supabase.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        tasa_db = db_actual[0] if db_actual else {}

        # 2. Actualizar tasa actual (Upsert)
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv_dolar": tasa_bcv_dolar,
            "bcv_euro": tasa_bcv_euro,
            "binance": tasa_binance_promedio
        }).execute()

        # 3. Historial inteligente (Insert)
        if tasa_bcv_euro != tasa_db.get('bcv_euro') or tasa_bcv_dolar != tasa_db.get('bcv_dolar'):
            fecha_actual = datetime.now().isoformat()
            datos_historial = [
                {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
                {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual}
            ]
            supabase.table("historial_tasas").insert(datos_historial).execute()
            print("🟩 Cambio detectado: Historial actualizado.")
        else:
            print("ℹ️ Sin cambios en BCV. Historial omitido.")

        print("🟩 Sincronización Exitosa.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    ejecutar_actualizacion()
