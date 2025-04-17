import requests
import datetime
import time
import pandas as pd
import os

def a_csv(precios, nombre_archivo):
    # df = pd.DataFrame(precios, columns=["Precio"])
    df = pd.DataFrame(precios, columns=["Fecha", "Precio"]) # Opcion para guardar la fecha tamb 
    df.to_csv(os.path.join("Precios BTC", nombre_archivo), index=False)
    print(f"Datos guardados en {nombre_archivo}")

def obtener_precios_historicos(symbol, interval, start_time, end_time):
    """Obtiene velas históricas desde Binance."""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000  # Binance permite un máximo de 1000 velas por solicitud
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Lanza un error si la solicitud falla
    data = response.json()
    return data

def convertir_a_timestamp(fecha_str):
    """Convierte una fecha en formato 'YYYY-MM-DD' a timestamp en milisegundos."""
    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(fecha.timestamp() * 1000)


symbol = "BTCUSDT"  # Par de trading
interval = "1h"  # Velas de 1 hora
start_date = "2023-01-01"  # Fecha de inicio (hace 6 meses, ajusta según necesidad)
end_date = "2023-12-31"  # Fecha de fin (hoy o cerca)

start_time = convertir_a_timestamp(start_date)
end_time = convertir_a_timestamp(end_date)

precios = []
while start_time < end_time:
    # Obtiene las velas en bloques de 1000
    data = obtener_precios_historicos(symbol, interval, start_time, end_time)
    if not data:
        break  # Si no hay más datos, sal del bucle
    
    # Extrae los precios de cierre
    # precios += [float(vela[4]) for vela in data]
    precios += [
        [datetime.datetime.utcfromtimestamp(vela[0] / 1000).strftime("%Y-%m-%d %H:%M:%S"), float(vela[4])]
        for vela in data]
    # Los datos llegan asi:
    # [
    # 1672531200000,  # Open time (timestamp en ms)
    # "30000.01",     # Precio de apertura
    # "30250.45",     # Precio más alto
    # "29900.23",     # Precio más bajo
    # "30150.89",     # Precio de cierre
    # "123.456",      # Volumen de trading
    # ...             # Otros datos (no relevantes aquí)
    # ] 
    # Por esta rzon tomamos el 4, que seria el precio de cierre
        
    # Actualiza el tiempo de inicio al cierre de la última vela
    start_time = data[-1][0] + 1  # Avanza al siguiente bloque de datos

    # Espera para evitar sobrecargar la API
    time.sleep(0.1)

print(f"Se obtuvieron {len(precios)} precios históricos.")
print(precios[:10])  # Imprime los primeros 10 precios como ejemplo
a_csv(precios, "Cotizaciones_2023.csv")