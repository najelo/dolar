import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_y_guardar_tasas():
    url = "https://www.bcv.org.ve/"
    
    # NUEVOS HEADERS MÁS HUMANOS
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="127", "Google Chrome";v="127"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    }

    try:
        # Simulamos una visita real
        time.sleep(random.uniform(5, 10))
        
        # USAMOS SESSION PARA MANTENER COOKIES
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, verify=False)
        
        # DEBUG: Imprimir si la página cargó bien
        print(f"DEBUG: Estado de respuesta {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- DIAGNÓSTICO PROFUNDO ---
        # Si no encuentra nada, vamos a ver qué hay en la página
        recuadros = soup.find_all('div', class_='recuadro_tipo_cambio')
        
        if not recuadros:
            # Imprimimos los IDs que existen para ver si cambiaron la estructura
            ids_divs = [div.get('id') for div in soup.find_all('div', id=True)]
            print(f"DEBUG: Ids encontrados en la web: {ids_divs[:20]}")
            print("❌ No se encontraron los recuadros. ¿Ha cambiado la web?")
            return

        datos = {}
        for item in recuadros:
            # ... (resto de tu lógica de extracción)
            nombre = item.find('label').text.strip()
            valor_raw = item.find('strong').text.strip()
            valor_num = float(valor_raw.replace(',', '.'))
            
            if "Dólar" in nombre: datos["bcv_dolar"] = valor_num
            elif "Euro" in nombre: datos["bcv_euro"] = valor_num
        
        # ... (resto de tu lógica de subida a Supabase)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    obtener_y_guardar_tasas()
