import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def actualizar_tasas_bcv():
    # 1. Usar una sesión persistente (simula que el navegador mantiene cookies/conexión)
    session = requests.Session()
    
    # 2. Lista más amplia de User-Agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/',
        'DNT': '1', # Do Not Track (opcional)
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })

    url = "https://www.bcv.org.ve/"
    
    try:
        # 3. Simular tiempo de carga de página real
        time.sleep(random.uniform(5, 12)) 
        
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status() # Verifica si la página cargó bien
        
        soup = BeautifulSoup(response.content, 'html.parser')
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # 4. Busqueda por contenido (más natural que solo buscar por ID)
        divs = soup.find_all('div', class_='recuadro_tipo_cambio')
        
        for div in divs:
            nombre = div.find('label').text.strip()
            valor = float(div.find('strong').text.strip().replace(',', '.'))
            
            if "Dólar" in nombre:
                supabase.table("tasas_monitoreo").update({"bcv_dolar": valor}).eq("id", 1).execute()
                print(f"✅ Dólar BCV detectado y guardado: {valor}")
            elif "Euro" in nombre:
                supabase.table("tasas_monitoreo").update({"bcv_euro": valor}).eq("id", 1).execute()
                print(f"✅ Euro BCV detectado y guardado: {valor}")

    except Exception as e:
        print(f"❌ El sitio del BCV pudo bloquear la petición o cambiar su estructura: {e}")

if __name__ == "__main__":
    actualizar_tasas_bcv()
