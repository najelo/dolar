import requests

def listar_todos_los_metodos():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "rows": 20, # Analizamos 20 anuncios para tener más variedad
        "page": 1
    }
    
    metodos_unicos = set() # Usamos un set para que no se repitan
    
    try:
        response = requests.post(url, json=payload, timeout=10).json()
        
        if "data" in response and response["data"]:
            for anuncio in response["data"]:
                # Cada anuncio puede tener múltiples métodos de pago
                for metodo in anuncio["adv"]["tradeMethods"]:
                    metodos_unicos.add(metodo["tradeMethodName"])
            
            print("--- Métodos de pago encontrados en el mercado ---")
            for m in sorted(metodos_unicos):
                print(f"Nombre interno: '{m}'")
        else:
            print("No se encontraron anuncios activos.")
            
    except Exception as e:
        print(f"Error al conectar con la API: {e}")

if __name__ == "__main__":
    listar_todos_los_metodos()
