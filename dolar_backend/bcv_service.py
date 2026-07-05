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

def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload, timeout=10)

def ejecutar_servicio():
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        if response.status_code != 200: return
        
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
                
                # 2. Notificar por Telegram usando el mismo script
                enviar_telegram(f"✅ *Tasa Actualizada*\n{nombre_banco}: *Bs. {valor_float}*")
                logging.info(f"ÉXITO: {nombre_banco} guardado y notificado.")

    except Exception as e:
        logging.error(f"CRÍTICO: {e}")
        enviar_telegram(f"❌ *Error en el Bot*: {str(e)}")

if __name__ == "__main__":
    ejecutar_servicio()
