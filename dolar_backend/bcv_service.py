import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

# Ignora advertencias de seguridad para evitar bloqueos por certificados SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    
    # 1. Headers que engañan al servidor haciéndole creer que eres un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Referer': 'https://www.google.com/'
    }

    try:
        # 2. Simulamos tiempo de carga de página
        time.sleep(random.uniform(3, 7))
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 3. Extracción específica de las tasas
        # El BCV agrupa las tasas en recuadros con esta clase
        tasas = {}
        recuadros = soup.find_all('div', class_='recuadro_tipo_cambio')

        for item in recuadros:
            nombre = item.find('label').text.strip()
            valor = item.find('strong').text.strip().replace(',', '.')
            if "Dólar" in nombre:
                tasas["bcv_dolar"] = float(valor)
            elif "Euro" in nombre:
                tasas["bcv_euro"] = float(valor)

        return tasas

    except Exception as e:
        print(f"❌ Error al extraer: {e}")
        return None

if __name__ == "__main__":
    datos = obtener_tasa_bcv()
    if datos:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
        print(f"✅ Tasa oficial BCV actualizada: {datos}")
