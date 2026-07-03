import os
import requests
import random
import time
import urllib3
import logging
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Configuración de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ejecutar_servicio():
    logging.info("Iniciando jornada de actualización BCV...")
    time.sleep(random.uniform(10, 20))
    
    url = "https://www.bcv.org.ve/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/127.0.0.0'
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=40, verify=False)
        
        if response.status_code != 200:
            logging.warning(f"El BCV no respondió (Código {response.status_code}).")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        datos = {}

        # 1. Extracción de tasas
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)
                logging.info(f"Éxito: {moneda} capturado: {valor_str}")
            else:
                logging.error(f"¡Atención! No encontré el contenedor de {moneda}.")
        
        # 2. Extracción de fecha (Buscando directamente en el bloque de fecha del BCV)
        fecha_div = soup.find('div', class_='pull-right')
        if fecha_div and fecha_div.find('span'):
            fecha_texto = fecha_div.find('span').text.strip()
            # Convertimos formato dd/mm/yyyy a formato ISO para la base de datos
            datos['fecha_bcv'] = datetime.strptime(fecha_texto, '%d/%m/%Y').isoformat()
            logging.info(f"Éxito: Fecha capturada: {datos['fecha_bcv']}")
        else:
            logging.error("No se pudo encontrar el contenedor de fecha.")

        # 3. Guardado en Supabase
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            logging.info("Resumen final: Tasas y fecha publicadas correctamente.")
        else:
            logging.error("No se pudo completar la actualización debido a datos incompletos.")

    except Exception as e:
        logging.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
