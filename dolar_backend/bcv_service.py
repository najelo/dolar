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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0.0.0 Safari/127.0.0.0'}

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=40, verify=False)
        if response.status_code != 200: return

        soup = BeautifulSoup(response.content, 'html.parser')
        datos = {}

        # 1. Extracción de tasas
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)

        # 2. Extracción de fecha (Lógica robusta)
        fecha_div = soup.find('div', class_='pull-right')
        if fecha_div and fecha_div.find('span'):
            raw_date = fecha_div.find('span').text.strip()
            # Ejemplo recibido: "Viernes, 03 Julio 2026"
            # Removemos el día de la semana y limpiamos
            clean_date = raw_date.split(',')[1].strip() if ',' in raw_date else raw_date
            
            # Diccionario de meses para traducir
            meses = {"Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06", 
                     "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}
            
            for nombre, numero in meses.items():
                if nombre in clean_date:
                    clean_date = clean_date.replace(nombre, numero)
            
            # Ahora clean_date es algo como "03 07 2026"
            # Convertimos a formato ISO
            datos['fecha_bcv'] = datetime.strptime(clean_date.replace(" ", "/"), '%d/%m/%Y').isoformat()
            logging.info(f"Éxito: Fecha capturada: {datos['fecha_bcv']}")

        # 3. Guardado
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            logging.info("Tasas y fecha publicadas.")

    except Exception as e:
        logging.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
