import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

def actualizar_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        # User-Agent para que el BCV no bloquee la petición
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # El precio del dólar en el BCV está en un div con id 'dolar'
        dolar_text = soup.find('div', id='dolar').find('strong').text
        tasa_bcv = float(dolar_text.replace(',', '.'))
        
        # Guardar en Supabase
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        supabase.table("tasas_monitoreo").update({"bcv": tasa_bcv}).eq("id", 1).execute()
        print(f"✅ Tasa BCV actualizada: {tasa_bcv}")
        
    except Exception as e:
        print(f"❌ Error al obtener BCV: {e}")

if __name__ == "__main__":
    actualizar_bcv()
