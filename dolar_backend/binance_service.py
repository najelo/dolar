import requests

def descubrir_metodos_pago():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "rows": 5, # Solo pedimos 5 filas para ver sus métodos de pago
        "page": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        if "data" in response and len(response["data"]) > 0:
            # Extraemos los métodos de pago del primer anuncio encontrado
            metodos = response["data"][0]["adv"]["tradeMethods"]
            print("--- Métodos de pago encontrados ---")
            for m in metodos:
                print(f"Nombre interno: {m['tradeMethodName']}")
        else:
            print("No se encontraron anuncios, intenta en otro momento.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    descubrir_metodos_pago()
