import os
import requests
import logging
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Configuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ejecutar_servicio():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    url = "https://www.bcv.org.ve/"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        if response.status_code != 200: return
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Extracción de valores
        tasas_nuevas = {}
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_str = div.find('strong').text.strip().replace(',', '.')
                tasas_nuevas[moneda] = float(valor_str)

        # 2. Extracción de fecha
        fecha_str = soup.find('div', class_='pull-right').find('span').text.strip()
        # Simplificación de fecha para formato ISO
        fecha_iso = datetime.now().isoformat() 

        # 3. Comparación y Guardado
        tasa_actual = supabase.table("tasas_monitoreo").select("*").eq("id", 1).execute().data[0]

        for moneda, valor in tasas_nuevas.items():
            nombre_banco = "BCV USD" if moneda == 'dolar' else "BCV EURO"
            campo_db = 'bcv_dolar' if moneda == 'dolar' else 'bcv_euro'

            # Si el valor cambió, guardamos en historial y actualizamos el principal
            if tasa_actual[campo_db] != valor:
                logging.info(f"Cambio detectado en {nombre_banco}. Guardando historial...")
                
                # Insertar en tabla historial_tasas
                supabase.table("historial_tasas").insert({
                    "banco": nombre_banco,
                    "valor": valor,
                    "fecha_bcv": fecha_iso
                }).execute()

                # Actualizar tasa actual
                supabase.table("tasas_monitoreo").update({campo_db: valor}).eq("id", 1).execute()
        
        logging.info("Proceso de monitoreo finalizado.")

    except Exception as e:
        logging.error(f"Error en ejecución: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
