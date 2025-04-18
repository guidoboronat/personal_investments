import pandas as pd
from binance import obtener_precios_historicos

symbol = "BTCUSDT"  # Par de trading
interval = "1h"  # Velas de 1 hora
start_date = "2024-01-01"  # Fecha de inicio (hace 6 meses, ajusta según necesidad)
end_date = "2024-12-31"  # Fecha de fin (hoy o cerca)

precios = pd.DataFrame(obtener_precios_historicos(symbol,interval,start_date,end_date))
print(precios)
precios.to_csv("/Users/guidoboronat/personal/repo trading/personal_investments/Base/Precios_2024_1h.csv")

