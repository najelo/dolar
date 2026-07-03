import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def actualizar_tasas_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Actualizar Dólar
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            tasa_dolar = float(dolar_div.find('strong').text.strip().replace(',', '.'))
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update({"bcv_dolar": tasa_dolar}).eq("id", 1).execute()
            print(f"✅ Dólar BCV actualizado: {tasa_dolar}")

        # 2. Actualizar Euro
        euro_div = soup.find('div', id='euro')
        if euro_div:
            tasa_euro = float(euro_div.find('strong').text.strip().replace(',', '.'))
            supabase.table("tasas_monitoreo").update({"bcv_euro": tasa_euro}).eq("id", 1).execute()
            print(f"✅ Euro BCV actualizado: {tasa_euro}")
        else:
            print("❌ No se encontró el div 'euro' en la página del BCV")
        
    except Exception as e:
        print(f"❌ Error al obtener tasas BCV: {e}")

if __name__ == "__main__":
    actualizar_tasas_bcv()
