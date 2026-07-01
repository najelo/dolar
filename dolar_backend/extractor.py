import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# GitHub Actions leerá esto desde los Secrets que configuraste
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Error: No se encontraron las credenciales en las variables de entorno.")

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ejecutar_actualizacion():
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando ciclo de extracción...")
        
        # --- AQUÍ VA TU LÓGICA DE EXTRACCIÓN ---
        # Mantendremos tus valores de ejemplo por ahora
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        tasa_bcv = 633.36
        
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        # ----------------------------------------

        # Guardar en Supabase
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv": tasa_bcv,
            "binance": tasa_binance_promedio,
            "binance_banesco": tasa_banesco,
            "binance_mercantil": tasa_mercantil,
            "binance_bdv": tasa_bdv,
            "binance_pagomovil": tasa_pagomovil
        }).execute()
        
        print("🟩 Sincronización Exitosa -> Datos guardados en Supabase.")

    except Exception as e:
        print(f"❌ Error al subir los datos a Supabase: {e}")
        exit(1) # Salir con error para que GitHub Actions lo marque en rojo

if __name__ == "__main__":
    print("🚀 Extractor Ejecutándose en GitHub Actions...")
    ejecutar_actualizacion()
    print("✅ Proceso terminado correctamente.")
