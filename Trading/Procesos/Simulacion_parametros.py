import pandas as pd
from Trading.acciones.bot_mark1 import Mark1
from acciones.bot_mark3 import Mark3
import matplotlib.pyplot as plt
import datetime
import os

# Leer precios desde el archivo CSV
df = pd.read_csv(r"C:\Users\Guido\Desktop\UDEMY\Trading\Precios BTC\Cotizaciones_2022_btc.csv")
precios = df["Precio"].tolist()  # Convierte la columna de precios en una lista
print(precios[:10])  # Muestra los primeros 10 precios




### SIMULACION MARK1
# rendimientos={
#         "corto":[],
#         "largo":[],
#         "rendimiento":[]
# }
# if __name__ == "__main__":
#     for i in range(1,11):
#         for j in range(11,26):

#             bot = Mark1(budget=1000,corto=i,largo=j)
#             for precio in precios:
#                 bot.agregar_precio(precio)
#                 bot.tomar_decision(precio)


#             df_historial = bot.mostrar_historial()
#             rendimientos["corto"].append(i)
#             rendimientos["largo"].append(j)
#             rendimientos["rendimiento"].append(df_historial["Rendimiento"].iloc[-1])
#             # df_historial.to_csv("rendimientos_mark1.csv",index=False)
#             # print(df_historial.head())

#     df = pd.DataFrame(rendimientos)
#     df.to_csv(os.path.join("Resultados", "Simulacion_rendimientos_Mark1_2024_15min.csv"),index=False)
#     # bot.graficar_rendimiento()


#### SIMULACION MARK3
rendimientos={
        "corto":[],
        "mediano":[],
        "largo":[],
        "rendimiento":[]
}

if __name__ == "__main__":
    for i in range(1,11):
        for j in range(11,26):

            bot = Mark3(budget=1000,corto=i,mediano=j,largo=75)
            for precio in precios:
                bot.agregar_precio(precio)
                bot.tomar_decision(precio)


            df_historial = bot.mostrar_historial()
            rendimientos["corto"].append(i)
            rendimientos["mediano"].append(j)
            rendimientos["largo"].append(75)
            rendimientos["rendimiento"].append(df_historial["Rendimiento"].iloc[-1])
            # df_historial.to_csv("rendimientos_mark1.csv",index=False)
            # print(df_historial.head())

    df = pd.DataFrame(rendimientos)
    df.to_csv(os.path.join("Resultados", "Simulacion_rendimientos_Mark3_2022.csv"),index=False)
    # bot.graficar_rendimiento()