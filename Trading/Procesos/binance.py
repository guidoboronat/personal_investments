import requests
import datetime
import pandas as pd
import time


def convertir_a_timestamp(fecha_str):
    """Convierte una fecha en formato 'YYYY-MM-DD' a timestamp en milisegundos."""
    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(fecha.timestamp() * 1000)

def timestamp_to_datetime(timestamp_ms):
    return datetime.datetime.fromtimestamp(timestamp_ms / 1000)


### obtener precios
def obtener_precios_historicos(symbol, interval, start_time, end_time):
    """Obtiene todas las velas históricas desde Binance entre dos fechas."""

    url = "https://api.binance.com/api/v3/klines"
    start_ts = convertir_a_timestamp(start_time)
    end_ts = convertir_a_timestamp(end_time)

    resultados = []

    while start_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ts,
            "endTime": end_ts,
            "limit": 1000
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            break  # no hay más datos

        for vela in data:
            resultados.append({
                "symbol": symbol,
                "interval": interval,
                "open_time": timestamp_to_datetime(vela[0]),
                "open_price": float(vela[1]),
                "high_price": float(vela[2]),
                "low_price": float(vela[3]),
                "close_price": float(vela[4]),
                "volume": float(vela[5]),
                "close_time": timestamp_to_datetime(vela[6]),
                "quote_volume": float(vela[7]),
                "num_trades": int(vela[8]),
                "taker_buy_base": float(vela[9]),
                "taker_buy_quote": float(vela[10])
            })

        # avanzar al siguiente lote de datos
        last_close_time = data[-1][6]
        start_ts = last_close_time + 1  # evitar solapamiento

        # opcional: prevenir rate limit
        time.sleep(0.2)

    return resultados
