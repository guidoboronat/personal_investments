import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Descargar datos
data = yf.download("AAPL", start="2024-06-01", end="2024-12-31", interval="1h")
precios_apple = data[["Close"]]

# Calcular medias móviles usando rolling()
precios_apple["mm_corto"] = precios_apple["Close"].rolling(window=5).mean()
precios_apple["mm_mediano"] = precios_apple["Close"].rolling(window=25).mean()
precios_apple["mm_largo"] = precios_apple["Close"].rolling(window=100).mean()

# Graficar
precios_apple.plot(figsize=(10, 6), title="Precios AAPL y Medias Móviles")
plt.xlabel("Fecha")
plt.ylabel("Precio / Media móvil")
plt.grid()
plt.show()
