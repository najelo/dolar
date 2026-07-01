import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def ejecutar_actualizacion():
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando ciclo de actualización...")
        
        # --- DATOS EXTRAÍDOS (Aquí iría tu lógica de scraping) ---
        tasa_bcv_dolar = 633.36
        tasa_bcv_euro = 723.27
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        fecha_actual = datetime.now().isoformat()

        # 1. Actualizar tabla principal (tasas_monitoreo)
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

        # 2. Insertar en tabla de historial (historial_tasas)
        datos_historial = [
            {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
            {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual},
            {"banco": "Binance Banesco", "valor": tasa_banesco, "fecha": fecha_actual},
            {"banco": "Binance Mercantil", "valor": tasa_mercantil, "fecha": fecha_actual},
            {"banco": "Binance BDV", "valor": tasa_bdv, "fecha": fecha_actual},
            {"banco": "Binance PagoMóvil", "valor": tasa_pagomovil, "fecha": fecha_actual}
        ]
        supabase.table("historial_tasas").insert(datos_historial).execute()
        
        print("🟩 Sincronización Exitosa: Tabla principal y registros históricos actualizados.")

    except Exception as e:
        print(f"❌ Error al subir los datos a Supabase: {e}")

if __name__ == "__main__":
    print("🚀 Extractor Automatizado Iniciado")
    while True:
        ejecutar_actualizacion()
        print("⏳ Esperando 15 minutos...")
        time.sleep(900)
