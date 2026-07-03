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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/127.0.0.0'}

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=40, verify=False)
        if response.status_code != 200: return

        soup = BeautifulSoup(response.content, 'html.parser')
        datos = {}

        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)

        fecha_div = soup.find('div', class_='date-display')
        if fecha_div:
            # Convierte formato "dd/mm/yyyy" a ISO "yyyy-mm-dd"
            fecha_texto = fecha_div.text.strip()
            datos['fecha_bcv'] = datetime.strptime(fecha_texto, '%d/%m/%Y').isoformat()

        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            logging.info("Tasas BCV actualizadas correctamente.")

    except Exception as e:
        logging.error(f"Error BCV: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
