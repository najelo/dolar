import os
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando ciclo de extracción...")
        
        # Tasas (Aquí colocarás tu lógica de scraping o valores)
        tasa_banesco = 734.89
        tasa_mercantil = 735.00
        tasa_bdv = 735.00
        tasa_pagomovil = 735.00
        tasa_binance_promedio = round((tasa_banesco + tasa_mercantil + tasa_bdv + tasa_pagomovil) / 4, 2)
        
        tasa_bcv_dolar = 633.36
        tasa_bcv_euro = 680.50 
        
        if tasa_bcv_euro <= 0 or tasa_bcv_dolar <= 0:
            print("❌ Error: Valores detectados como 0 o negativos. Abortando.")
            return

        # 1. Obtener estado actual en Supabase
        db_actual = supabase.table("tasas_monitoreo").select("*").eq("id", 1).execute().data
        tasa_db = db_actual[0] if db_actual else {}

        # 2. Actualizar tasa actual (Upsert)
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

        # 3. Historial inteligente (Insert)
        if tasa_bcv_euro != tasa_db.get('bcv_euro') or tasa_bcv_dolar != tasa_db.get('bcv_dolar'):
            fecha_actual = datetime.now().isoformat()
            datos_historial = [
                {"banco": "BCV Dólar", "valor": tasa_bcv_dolar, "fecha": fecha_actual},
                {"banco": "BCV Euro", "valor": tasa_bcv_euro, "fecha": fecha_actual},
                {"banco": "BINANCE", "valor": tasa_binance_promedio, "fecha": fecha_actual}
            ]
            supabase.table("historial_tasas").insert(datos_historial).execute()
            print("🟩 Cambio detectado: Historial actualizado.")
        else:
            print("ℹ️ Sin cambios. Historial omitido.")

        print("🟩 Sincronización Exitosa.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    ejecutar_actualizacion()
