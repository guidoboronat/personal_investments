import requests
import time
from collections import deque
from datetime import datetime,timedelta
import pandas as pd
import matplotlib.pyplot as plt

def calcular_rsi(lista):
    # Cambios de precios
    cambios = [lista[i] - lista[i-1] for i in range(1, len(lista))]
    ganancias = []
    perdidas = []

    # Separar ganancias y pérdidas
    for x in cambios:
        if x > 0:
            ganancias.append(x)
        elif x < 0:
            perdidas.append(-x)

    # Promedios de ganancias y pérdidas
    promedio_ganancias = sum(x if x > 0 else 0 for x in cambios) / len(lista)
    promedio_perdidas = sum(-x if x < 0 else 0 for x in cambios) / len(lista)

    # Calcular RS y RSI
    rs = promedio_ganancias / promedio_perdidas if promedio_perdidas != 0 else float('inf')
    rsi = 100 - (100 / (1 + rs))

    return rsi



class Mark4:
    def __init__(self, budget,corto,mediano,largo,rsi_limit):
        self.budget = budget  # Capital inicial en USDT
        self.budget_inicial = budget
        self.corto = corto
        self.mediano = mediano
        self.largo = largo
        self.rsi_limit = rsi_limit
        self.crypto_balance = 0  # Cantidad de criptomonedas en posesión
        self.prices = deque(maxlen=largo)  # Mantiene un historial de hasta 25 precios
        self.last_action = None  # Guarda la última acción: 'buy', 'sell' o None
        self.ganancia_perdida_acumulada = 0  # Ganancia/Pérdida total acumulada
        self.rendimiento_porcentaje = 0
        self.historial_operaciones = []  # Registro de operaciones
        self.precio_compra = None  # Precio al que se realizó la última compra
        # if isinstance(start_time, str):
        #     self.current_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        # else:
        #     self.current_time = start_time or datetime.now()

    def agregar_precio(self, precio):
        """Agrega el precio actual al historial."""
        self.prices.append(precio)

    def calcular_media_movil(self, periodos):
        """Calcula la media móvil para los últimos 'periodos' precios."""
        if len(self.prices) < periodos:
            return None  # No hay suficientes datos para calcular la media móvil
        return sum(list(self.prices)[-periodos:]) / periodos

    def registrar_operacion(self, operacion, precio, cantidad):
        """Registra una operación de compra o venta en el historial."""
        # fecha = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.historial_operaciones.append({
            # "Fecha": fecha,
            "Operación": operacion,
            "Precio": precio,
            "Cantidad": cantidad,
            "Budget": self.budget,
            "Crypto": self.crypto_balance,
            "Ganancia/Pérdida Acumulada": self.ganancia_perdida_acumulada,
            "Rendimiento": self.rendimiento_porcentaje
        })

    def tomar_decision(self, precio_actual):
        """Decide si comprar, vender o no hacer nada."""
        # Calcula las medias móviles de corto y mediano plazo
        mm_corto = self.calcular_media_movil(self.corto)
        mm_mediano = self.calcular_media_movil(self.mediano)
        mm_largo = self.calcular_media_movil(self.largo)
        rsi = calcular_rsi(list(self.prices)[-14:])
        



        if (mm_corto is None or mm_mediano is None 
            # or mm_largo is None
            ):
            # if self.current_time:
            #     self.current_time += timedelta(hours=1)
            return  # No toma decisiones si no hay suficientes datos
        
        # Agregamos condicion para ver si nos encontramos en una tendencia alcista o bajista, solo operamos en la alcista
        # if mm_mediano < mm_largo:
        #     # if self.current_time:
        #     #     self.current_time += timedelta(hours=1)
        #     return 

        if (rsi > self.rsi_limit and self.crypto_balance > 0 and self.last_action != 'sell'):
            valor_venta = self.crypto_balance * precio_actual
            ganancia_perdida = valor_venta - (self.precio_compra * self.crypto_balance)
            self.ganancia_perdida_acumulada += ganancia_perdida
            self.rendimiento_porcentaje = self.ganancia_perdida_acumulada/self.budget_inicial
            self.budget = valor_venta
            cantidad_vendida = self.crypto_balance
            self.crypto_balance = 0
            self.last_action = 'sell'
            print(f"Venta realizada: {self.budget:.2f} USDT a {precio_actual} USDT")
            self.registrar_operacion("Venta", precio_actual, cantidad_vendida)


        # Lógica de trading
        elif mm_corto > mm_mediano and self.budget > 0 and self.last_action != 'buy':
            # Comprar todo el budget
            self.crypto_balance = self.budget / precio_actual
            self.precio_compra = precio_actual
            self.budget = 0
            self.last_action = 'buy'
            print(f"Compra realizada: {self.crypto_balance:.6f} unidades a {precio_actual} USDT")
            self.registrar_operacion("Compra", precio_actual, self.crypto_balance)
        
        elif (mm_corto < mm_mediano and self.crypto_balance > 0 and self.last_action != 'sell'):
            # Vender todo
            valor_venta = self.crypto_balance * precio_actual
            ganancia_perdida = valor_venta - (self.precio_compra * self.crypto_balance)
            self.ganancia_perdida_acumulada += ganancia_perdida
            self.rendimiento_porcentaje = self.ganancia_perdida_acumulada/self.budget_inicial
            self.budget = valor_venta
            cantidad_vendida = self.crypto_balance
            self.crypto_balance = 0
            self.last_action = 'sell'
            print(f"Venta realizada: {self.budget:.2f} USDT a {precio_actual} USDT")
            self.registrar_operacion("Venta", precio_actual, cantidad_vendida)
            
        # if self.current_time:
        #     self.current_time += timedelta(hours=1)

    def estado_actual(self):
        """Imprime el estado actual del bot."""
        print(f"Budget: {self.budget:.2f} USDT")
        print(f"Balance cripto: {self.crypto_balance:.6f} unidades")
        print(f"Última acción: {self.last_action}")


    def mostrar_historial(self):
        """Muestra el historial de operaciones como un DataFrame."""
        df = pd.DataFrame(self.historial_operaciones)
        print(df)
        return df

    def graficar_rendimiento(self):
        """Genera un gráfico del rendimiento acumulado."""
        df = pd.DataFrame(self.historial_operaciones)
        if "Rendimiento" in df.columns:
            df["Rendimiento"].plot(kind="line", figsize=(10, 6))
            plt.title("Rendimiento Acumulado del Bot")
            plt.xlabel("Operación")
            plt.ylabel("Ganancia/Pérdida Acumulada (USDT)")
            plt.grid()
            plt.show()
        else:
            print("No hay suficientes datos para graficar el rendimiento.")
