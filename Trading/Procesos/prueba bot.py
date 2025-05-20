import pandas as pd
from Trading.acciones.bot_mark1 import Mark1
from acciones.bot_mark4 import Mark4
import matplotlib.pyplot as plt
import datetime
import os


# Leer precios desde el archivo CSV
df = pd.read_csv(r"C:\Users\Guido\Desktop\UDEMY\Trading\Precios BTC\Cotizaciones_2024_15min_btc.csv")
precios = df["Precio"].tolist()  # Convierte la columna de precios en una lista
print(precios[:10])  # Muestra los primeros 10 precios


# if __name__ == "__main__":


#     bot = Mark1(budget=1000,corto=7,largo=16)
#     for precio in precios:
#         bot.agregar_precio(precio)
#         bot.tomar_decision(precio)

#     df_historial = bot.mostrar_historial()
#     # df_historial.to_csv("rendimientos_mark1.csv",index=False)
#     print(df_historial.head())
#     df_historial.to_csv(os.path.join("Resultados", "Mark1_2024_15min.csv"),index=False)
#     # bot.graficar_rendimiento()

if __name__ == "__main__":

    bot = Mark4(budget=1000,corto=10,mediano=11,largo=75,rsi_limit=1)
    for precio in precios:
        bot.agregar_precio(precio)
        bot.tomar_decision(precio)
        bot.estado_actual()


    df_historial = bot.mostrar_historial()
    df_historial.to_csv("rendimientos_Mark4.csv",index=False)
    print(df_historial.head())

    # bot.graficar_rendimiento()