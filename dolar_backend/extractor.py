import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde el archivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Error: No se encontraron las credenciales en el archivo .env")

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ejecutar_actualizacion():
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando ciclo de extracción de divisas...")
        
        # --- AQUÍ EXTRAES TUS DATOS REALES (Mapeados desde tu lógica de Selenium/Scraping) ---
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        tasa_bcv = 633.36
        
        # Calcular el promedio general para mantener la tarjeta principal
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        # ----------------------------------------------------------------------------------

        # Guardar todo de forma desglosada en la fila ID 1
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv": tasa_bcv,
            "binance": tasa_binance_promedio,
            "binance_banesco": tasa_banesco,
            "binance_mercantil": tasa_mercantil,
            "binance_bdv": tasa_bdv,
            "binance_pagomovil": tasa_pagomovil
        }).execute()
        
        print("🟩 Sincronización Exitosa -> Todos los bancos guardados en la fila 1 de Supabase.")

    except Exception as e:
        print(f"❌ Error al subir los datos a Supabase: {e}")

if __name__ == "__main__":
    print("=====================================================")
    print("🚀 Extractor Automatizado de Divisas (Modo Desglosado)")
    print("=====================================================")
    
    while True:
        ejecutar_actualizacion()
        print("⏳ Esperando 15 minutes para la próxima verificación...")
        time.sleep(900)