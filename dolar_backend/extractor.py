import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Error: No se encontraron las credenciales.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ejecutar_actualizacion():
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando ciclo de extracción...")
        
        # Tasas (simuladas o extraídas)
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        tasa_bcv_dolar = 633.36
        tasa_bcv_euro = 680.50
        
        # Fecha actual para el historial
        fecha_actual = datetime.now().isoformat()

        # 1. Actualizar tasa actual
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv_dolar": tasa_bcv_dolar,
            "bcv_euro": tasa_bcv_euro,
            "binance": tasa_binance_promedio,
            "binance_banesco": tasa_banesco,
            "binance_mercantil": tasa_mercantil,
            "binance_bdv": tasa_bdv,
            "binance_pagomovil": tasa_pagomovil
        }).execute()

        # 2. Insertar historial con el campo 'fecha'
        datos_historial = [
            {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
            {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual},
            {"banco": "BINANCE", "valor": tasa_binance_promedio, "fecha": fecha_actual},
            {"banco": "Binance - Banesco", "valor": tasa_banesco, "fecha": fecha_actual},
            {"banco": "Binance - Mercantil", "valor": tasa_mercantil, "fecha": fecha_actual},
            {"banco": "Binance - BDV", "valor": tasa_bdv, "fecha": fecha_actual},
            {"banco": "Binance - PagoMóvil", "valor": tasa_pagomovil, "fecha": fecha_actual}
        ]
        
        supabase.table("historial_tasas").insert(datos_historial).execute()
        
        print("🟩 Sincronización Exitosa.")

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    ejecutar_actualizacion()
