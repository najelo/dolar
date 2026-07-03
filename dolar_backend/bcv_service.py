import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_headers():
    # Lista de navegadores reales para rotar
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive'
    }

def actualizar_tasas_bcv():
    # Pausa aleatoria inicial para simular un inicio de navegación humano
    time.sleep(random.uniform(2, 6))
    
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, headers=get_headers(), timeout=20, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # 1. Actualizar Dólar
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            tasa_dolar = float(dolar_div.find('strong').text.strip().replace(',', '.'))
            supabase.table("tasas_monitoreo").update({"bcv_dolar": tasa_dolar}).eq("id", 1).execute()
            print(f"✅ Dólar BCV actualizado: {tasa_dolar}")
        
        # Pausa aleatoria entre lecturas
        time.sleep(random.uniform(1, 3))

        # 2. Actualizar Euro
        euro_div = soup.find('div', id='euro')
        if euro_div:
            tasa_euro = float(euro_div.find('strong').text.strip().replace(',', '.'))
            supabase.table("tasas_monitoreo").update({"bcv_euro": tasa_euro}).eq("id", 1).execute()
            print(f"✅ Euro BCV actualizado: {tasa_euro}")
        else:
            print("❌ No se encontró el div 'euro'")
            
    except Exception as e:
        print(f"❌ Error al obtener tasas BCV: {e}")

if __name__ == "__main__":
    actualizar_tasas_bcv()
