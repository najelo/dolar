import requests
import random
import time

def diagnostico_rapido():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"asset": "USDT", "fiat": "VES", "rows": 20, "page": 1}
    
    print("🤖 Bot: Diagnosticando el mercado...")
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json().get("data", [])
        
        if not data:
            print("🤖 Bot: La API no devolvió datos. ¿Bloqueo de IP?")
            return

        # Solo miramos los primeros 5 anuncios
        for i, a in enumerate(data[:5]):
            metodos = [m.get("tradeMethodName") for m in a["adv"].get("tradeMethods", [])]
            precio = a["adv"].get("price")
            print(f"Anuncio {i+1}: Precio {precio} | Métodos: {metodos}")
            
    except Exception as e:
        print(f"Error técnico: {e}")

diagnostico_rapido()
