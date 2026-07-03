import os
import requests
from supabase import create_client

def actualizar_tasas():
    # Ya no necesitas headers, user-agents ni simulaciones
    API_KEY = os.getenv("API_KEY_EXCHANGE") 
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    
    try:
        # Petición directa y limpia
        response = requests.get(url)
        data = response.json()
        
        if data["result"] == "success":
            tasa_usd_ves = data["conversion_rates"]["VES"]
            # Calcular euro (tasa cruzada)
            tasa_eur_usd = data["conversion_rates"]["EUR"]
            tasa_eur_ves = tasa_usd_ves / tasa_eur_usd
            
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            supabase.table("tasas_monitoreo").update({
                "bcv_dolar": tasa_usd_ves,
                "bcv_euro": tasa_eur_ves
            }).eq("id", 1).execute()
            
            print(f"✅ Éxito: {tasa_usd_ves} VES/USD")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    actualizar_tasas()
