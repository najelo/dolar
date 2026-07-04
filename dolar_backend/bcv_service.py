import os
import requests
import logging
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Configuración de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ejecutar_servicio():
    logging.info("--- INICIANDO PROCESO DE EXTRACCIÓN ---")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        logging.info(f"Conectando a {url}...")
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        
        if response.status_code != 200:
            logging.error(f"Error de conexión: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Procesar divisas
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_raw = div.find('strong').text.strip()
                valor_float = float(valor_raw.replace(',', '.'))
                nombre_banco = "BCV USD" if moneda == 'dolar' else "BCV EURO"
                
                # --- AQUÍ ESTÁ EL CAMBIO ---
                # Usamos una única columna: fecha_registro
                payload = {
                    "banco": nombre_banco,
                    "valor": valor_float,
                    "fecha_registro": datetime.now().isoformat() 
                }
                
                logging.info(f"Guardando: {nombre_banco} | Valor: {valor_float}")
                supabase.table("historial_tasas").insert(payload).execute()
                logging.info("ÉXITO: Registro insertado con fecha estandarizada.")
            else:
                logging.warning(f"No se encontró: {moneda}")

        logging.info("--- PROCESO FINALIZADO ---")

    except Exception as e:
        logging.error(f"CRÍTICO: Error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
