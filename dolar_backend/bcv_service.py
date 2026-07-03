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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    try:
        time.sleep(random.uniform(5, 10))
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        datos = {}

        # Buscamos por ID, que es lo que el log nos confirmó que existe
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                # El valor suele estar dentro de un strong
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)
                print(f"✅ Encontrado {moneda}: {valor_str}")
            else:
                print(f"❌ No se pudo encontrar el div con id='{moneda}'")

        # Guardado en Supabase
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            print(f"🚀 Datos guardados exitosamente: {datos}")
        else:
            print("❌ No se recolectó ninguna tasa.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    obtener_y_guardar_tasas()import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_y_guardar_tasas():
    url = "https://www.bcv.org.ve/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    try:
        time.sleep(random.uniform(5, 10))
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        datos = {}

        # Buscamos por ID, que es lo que el log nos confirmó que existe
        for moneda in ['dolar', 'euro']:
            div = soup.find('div', id=moneda)
            if div:
                # El valor suele estar dentro de un strong
                valor_str = div.find('strong').text.strip().replace(',', '.')
                datos[f"bcv_{moneda}"] = float(valor_str)
                print(f"✅ Encontrado {moneda}: {valor_str}")
            else:
                print(f"❌ No se pudo encontrar el div con id='{moneda}'")

        # Guardado en Supabase
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            print(f"🚀 Datos guardados exitosamente: {datos}")
        else:
            print("❌ No se recolectó ninguna tasa.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    obtener_y_guardar_tasas()
