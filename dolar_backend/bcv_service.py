import os
import requests
import logging
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Configuración del log para que sea muy informativo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ejecutar_servicio():
    logging.info("--- INICIANDO PROCESO DE EXTRACCIÓN ---")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        logging.info("Conexión con Supabase establecida.")

        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        logging.info(f"Conectando a {url}...")
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        
        if response.status_code != 200:
            logging.error(f"Error de conexión: Código {response.status_code}")
            return
        
        logging.info("Página cargada correctamente. Procesando HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Procesar divisas
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_raw = div.find('strong').text.strip()
                valor_float = float(valor_raw.replace(',', '.'))
                nombre_banco = "BCV USD" if moneda == 'dolar' else "BCV EURO"
                
                logging.info(f"Dato detectado: {nombre_banco} | Valor original: {valor_raw} | Convertido: {valor_float}")
                
                # Guardado en historial
                payload = {
                    "banco": nombre_banco,
                    "valor": valor_float,
                    "fecha_bcv": datetime.now().isoformat()
                }
                
                logging.info(f"Intentando guardar en tabla 'historial_tasas': {payload}")
                supabase.table("historial_tasas").insert(payload).execute()
                logging.info(f"ÉXITO: {nombre_banco} guardado correctamente.")
            else:
                logging.warning(f"No se encontró el elemento HTML para: {moneda}")

        logging.info("--- PROCESO FINALIZADO CON ÉXITO ---")

    except Exception as e:
        logging.error(f"CRÍTICO: Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_servicio()
