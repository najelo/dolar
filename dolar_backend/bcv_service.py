import os
import requests
import logging
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enviar_telegram(mensaje):
    """Envía un mensaje a tu bot de Telegram."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logging.warning("Credenciales de Telegram no configuradas, omitiendo notificación.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        logging.error(f"Error al enviar a Telegram: {e}")

def ejecutar_servicio():
    logging.info("--- INICIANDO PROCESO DE EXTRACCIÓN BCV ---")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        if response.status_code != 200:
            logging.error(f"Error de conexión con BCV: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')

        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                valor_raw = div.find('strong').text.strip()
                valor_float = float(valor_raw.replace(',', '.'))
                nombre_banco = "BCV USD" if moneda == 'dolar' else "BCV EURO"
                
                payload = {
                    "banco": nombre_banco,
                    "valor": valor_float,
                    "fecha_registro": datetime.now().isoformat()
                }
                
                # 1. Guardar en Supabase
                supabase.table("historial_tasas").insert(payload).execute()
                logging.info(f"Guardado en Supabase: {nombre_banco} | {valor_float}")
                
                # 2. Notificar por Telegram
                enviar_telegram(f"✅ *Tasa Actualizada*\n{nombre_banco}: *Bs. {valor_float}*")
                
            else:
                logging.warning(f"No se encontró el elemento: {moneda}")

        logging.info("--- PROCESO FINALIZADO CON ÉXITO ---")

    except Exception as e:
        error_msg = f"❌ *Error crítico en el Bot BCV*: {str(e)}"
        logging.error(error_msg)
        enviar_telegram(error_msg)

if __name__ == "__main__":
    ejecutar_servicio()
