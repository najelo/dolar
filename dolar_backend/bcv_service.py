import os
import requests
import random
import time
import urllib3
import logging
from bs4 import BeautifulSoup
from supabase import create_client

# Configuración de log "humano"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ejecutar_servicio():
    logging.info("Iniciando jornada de actualización de tasas...")
    
    time.sleep(random.uniform(10, 20))
    
    url = "https://www.bcv.org.ve/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/127.0.0.0'
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=40, verify=False)
        
        if response.status_code != 200:
            logging.warning(f"El BCV no respondió como esperábamos (Código {response.status_code}).")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        datos = {}

        # Extracción de tasas
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)
                logging.info(f"Éxito: Tasa de {moneda} capturada: {valor_str}")
            else:
                logging.error(f"¡Atención! No encontré el contenedor de {moneda}.")
        
        # --- NUEVA EXTRACCIÓN DE FECHA ---
        fecha_div = soup.find('div', class_='date-display')
        if fecha_div:
            datos['fecha_bcv'] = fecha_div.text.strip()
            logging.info(f"Éxito: Fecha capturada: {datos['fecha_bcv']}")
        # ---------------------------------

        # Guardado en Supabase
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            logging.info("Resumen final: Tasas y fecha publicadas en base de datos correctamente.")
        else:
            logging.error("No se pudo completar la actualización debido a datos incompletos.")

    except Exception as e:
        logging.error(f"Se ha producido un error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
