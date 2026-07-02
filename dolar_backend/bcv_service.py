import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
import urllib3

# Desactivar advertencias de seguridad por el certificado SSL (que no podemos validar)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def actualizar_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        # Agregamos verify=False para saltar el error del certificado
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscamos el div con id 'dolar' y extraemos el texto del 'strong' dentro
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            dolar_text = dolar_div.find('strong').text.strip()
            # Reemplazamos coma por punto y convertimos a float
            tasa_bcv = float(dolar_text.replace(',', '.'))
            
            # Guardar en Supabase
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            supabase.table("tasas_monitoreo").update({"bcv_dolar": tasa_bcv}).eq("id", 1).execute()
            print(f"✅ Tasa BCV actualizada: {tasa_bcv}")
        else:
            print("❌ No se encontró el div 'dolar' en la página del BCV")
        
    except Exception as e:
        print(f"❌ Error al obtener BCV: {e}")

if __name__ == "__main__":
    actualizar_bcv()
