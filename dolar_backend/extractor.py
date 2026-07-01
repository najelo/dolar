import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Validación rápida de variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL o SUPABASE_KEY no configurados.")
    sys.exit(1)

supabase: Client = create_client(url, key)

def ejecutar_actualizacion():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando actualización...")
        
        # --- AQUÍ IRÍA TU LÓGICA DE SCRAPING ---
        tasa_bcv_dolar = 633.36
        tasa_bcv_euro = 723.27
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        fecha_actual = datetime.now().isoformat()

        # 1. Actualizar tabla principal
        supabase.table("tasas_monitoreo").upsert({
            "id": 1,
            "bcv_dolar": tasa_bcv_dolar,
            "bcv_euro": tasa_bcv_euro,
            "binance": tasa_binance_promedio,
            "binance_banesco": tasa_banesco,
            "binance_mercantil": tasa_mercantil,
            "binance_bdv": tasa_bdv,
            "binance_pagomovil": tasa_pagomovil,
            "ultima_actualizacion": fecha_actual
        }).execute()

        # 2. Insertar historial
        datos_historial = [
            {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
            {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual},
            {"banco": "Binance Banesco", "valor": tasa_banesco, "fecha": fecha_actual},
            {"banco": "Binance Mercantil", "valor": tasa_mercantil, "fecha": fecha_actual},
            {"banco": "Binance BDV", "valor": tasa_bdv, "fecha": fecha_actual},
            {"banco": "Binance PagoMóvil", "valor": tasa_pagomovil, "fecha": fecha_actual}
        ]
        supabase.table("historial_tasas").insert(datos_historial).execute()
        
        print("🟩 Sincronización Exitosa.")

    except Exception as e:
        print(f"❌ Error al subir los datos a Supabase: {e}")
        sys.exit(1) # Importante: salir con error si falla

if __name__ == "__main__":
    ejecutar_actualizacion()
