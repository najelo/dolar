import os
import requests
import random
import time
import urllib3
from bs4 import BeautifulSoup
from supabase import create_client

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_y_guardar_tasas():
    url = "https://www.bcv.org.ve/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    try:
        # 1. Navegación "humana"
        time.sleep(random.uniform(3, 7))
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 2. Extracción de datos
        recuadros = soup.find_all('div', class_='recuadro_tipo_cambio')
        datos = {}
        
        for item in recuadros:
            nombre = item.find('label').text.strip()
            valor_raw = item.find('strong').text.strip()
            valor_num = float(valor_raw.replace(',', '.'))
            
            print(f"DEBUG: Encontré '{nombre}' -> {valor_num}")
            
            if "Dólar" in nombre:
                datos["bcv_dolar"] = valor_num
            elif "Euro" in nombre:
                datos["bcv_euro"] = valor_num
        
        # 3. Guardado en Supabase (Solo si encontramos datos)
        if datos:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # Usamos .update() para tu fila id=1
            resultado = supabase.table("tasas_monitoreo").update(datos).eq("id", 1).execute()
            print(f"✅ Éxito total. Datos enviados a Supabase: {datos}")
        else:
            print("❌ Error: No se encontraron tasas en el HTML.")

    except Exception as e:
        print(f"❌ Error crítico en el proceso: {e}")

if __name__ == "__main__":
    obtener_y_guardar_tasas()
