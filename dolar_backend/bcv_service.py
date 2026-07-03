import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

# Deshabilitar advertencias de conexión segura
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def actualizar_tasas_bcv():
    # Sesión persistente para simular comportamiento de navegador
    session = requests.Session()
    
    # Lista de User-Agents para rotar y evitar detección
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ]
    
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })

    url = "https://www.bcv.org.ve/"
    
    try:
        # Pausa aleatoria inicial para parecer usuario real
        time.sleep(random.uniform(5, 12))
        
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Conexión a Supabase
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Buscar recuadros de cambio
        divs = soup.find_all('div', class_='recuadro_tipo_cambio')
        
        for div in divs:
            try:
                nombre = div.find('label').text.strip()
                valor_str = div.find('strong').text.strip().replace(',', '.')
                valor = float(valor_str)
                
                if "Dólar" in nombre:
                    supabase.table("tasas_monitoreo").update({"bcv_dolar": valor}).eq("id", 1).execute()
                    print(f"✅ Dólar BCV actualizado: {valor}")
                elif "Euro" in nombre:
                    supabase.table("tasas_monitoreo").update({"bcv_euro": valor}).eq("id", 1).execute()
                    print(f"✅ Euro BCV actualizado: {valor}")
            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Error al conectar con el BCV: {e}")

if __name__ == "__main__":
    actualizar_tasas_bcv()
