import os
import requests
from supabase import create_client

def actualizar_bcv():
    # 1. Configuración de Supabase
    url_supabase = os.getenv("SUPABASE_URL")
    key_supabase = os.getenv("SUPABASE_KEY")
    
    if not url_supabase or not key_supabase:
        print("❌ Error: Variables de entorno no configuradas")
        return

    supabase = create_client(url_supabase, key_supabase)
    
    # 2. Fuente de datos estática (No bloqueable)
    url_json = "https://raw.githubusercontent.com/fuchibol/pydolarvenezuela/main/assets/data/currencies.json"
    
    try:
        response = requests.get(url_json, timeout=15)
        response.raise_for_status() # Verifica si hubo error en la petición
        data = response.json()
        
        # Extraemos el valor
        precio_bcv = float(data['bcv']['dolar']['price'])
        
        # 3. Actualización en Supabase
        # id=1 es tu registro principal, ajusta si tu tabla usa otro ID
        resultado = supabase.table("tasas_monitoreo").update({"bcv_dolar": precio_bcv}).eq("id", 1).execute()
        
        print(f"✅ BCV actualizado exitosamente a: {precio_bcv}")
        
    except Exception as e:
        print(f"❌ Error crítico en el proceso de actualización: {e}")

if __name__ == "__main__":
    actualizar_bcv()
