import requests
import time
from collections import deque
from datetime import datetime,timedelta
import pandas as pd
import matplotlib.pyplot as plt

class Mark2:
    def __init__(self, budget, start_time=None):
        self.budget_inicial = budget  # Capital inicial en USDT
        self.budget = budget  # Capital inicial en USDT
        self.crypto_balance = 0  # Cantidad de criptomonedas en posesión
        self.prices = deque(maxlen=100)  # Mantiene un historial de hasta 100 precios
        self.last_action = None  # Guarda la última acción: 'buy', 'sell' o None
        self.ganancia_perdida_acumulada = 0  # Ganancia/Pérdida total acumulada
        self.historial_operaciones = []  # Registro de operaciones
        self.precio_compra = None  # Precio al que se realizó la última compra

        if isinstance(start_time, str):
            self.current_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.current_time = start_time or datetime.now()

    def agregar_precio(self, precio):
        """Agrega el precio actual al historial."""
        self.prices.append(precio)

    def calcular_media_movil(self, periodos):
        """Calcula la media móvil para los últimos 'periodos' precios."""
        if len(self.prices) < periodos:
            return None  # No hay suficientes datos para calcular la media móvil
        return sum(list(self.prices)[-periodos:]) / periodos
    
    def calcular_media_movil_prev(self, periodos):
        """Calcula la media móvil para los últimos 'periodos' precios."""
        if len(self.prices) < periodos + 1:
            return None  # No hay suficientes datos para calcular la media móvil
        precios_previos = list(self.prices)[:-1]  # Excluye el precio más reciente
        return sum(precios_previos[-periodos:]) / periodos


    def registrar_operacion(self, operacion, precio, cantidad):
        """Registra una operación de compra o venta en el historial."""
        fecha = self.current_time.strftime("%Y-%m-%d %H:%M:%S") if self.current_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ganancia_perdida_no_realizada = self.crypto_balance * precio  # Saldo cripto x precio actual
        ganancia_perdida_acumulada = self.budget + ganancia_perdida_no_realizada - self.budget_inicial  # Diferencia entre budget actual e inicial
        
        self.historial_operaciones.append({
            "Fecha": fecha,
            "Operación": operacion,
            "Precio": precio,
            "Cantidad": cantidad,
            "Budget": self.budget,
            "Crypto": self.crypto_balance,
            "Ganancia/Pérdida no realizada": ganancia_perdida_no_realizada,
            "Ganancia/Pérdida acumulada": ganancia_perdida_acumulada
        })

    def tomar_decision(self, precio_actual):
        """Decide si comprar, vender o no hacer nada."""
        # Calcula las medias móviles
        mm_corto = self.calcular_media_movil(7)
        mm_mediano = self.calcular_media_movil(25)
        mm_largo = self.calcular_media_movil(100)
        mm_mediano_prev = self.calcular_media_movil_prev(25)
        mm_largo_prev = self.calcular_media_movil_prev(100)

        if (mm_corto is None 
            or mm_mediano is None 
            or mm_largo is None 
            or mm_mediano_prev is None
            or mm_largo_prev is None):
            # Incrementa la hora en simulación
            if self.current_time:
                self.current_time += timedelta(hours=1)
            return  # No toma decisiones si no hay suficientes datos
        
        # Lógica de compra
        if mm_mediano > mm_largo and mm_mediano_prev < mm_largo_prev and self.budget > 0:
            # Compra el restante del budget
            self.precio_compra = precio_actual
            cantidad_comprada = self.budget / precio_actual
            self.crypto_balance += cantidad_comprada
            self.last_action = 'buy'
            self.budget = 0
            self.registrar_operacion("Compra (100%)", precio_actual, cantidad_comprada)
            return


        if mm_corto > mm_largo and mm_mediano > mm_largo and mm_corto > mm_mediano and self.budget > 0:
            # Compra el 100% del budget
            self.precio_compra = precio_actual
            cantidad_comprada = self.budget / precio_actual
            self.crypto_balance += cantidad_comprada
            self.last_action = 'buy'
            self.budget = 0
            self.registrar_operacion("Compra (100%)", precio_actual, cantidad_comprada)
            return


        if (mm_corto < mm_largo 
            and mm_mediano < mm_largo # es redundante esta pero para entender es mas facil
            and mm_corto > mm_mediano 
            and mm_mediano_prev < mm_largo_prev
            and self.budget > 0 
            and self.last_action != "buy-50"):
            # Compra 50% del budget
            self.precio_compra = precio_actual
            cantidad_comprada = (self.budget * 0.5) / precio_actual
            self.crypto_balance += cantidad_comprada
            self.last_action = "buy-50"
            self.budget *= 0.5
            self.registrar_operacion("Compra (50%)", precio_actual, cantidad_comprada)
            return



        # Lógica de venta
        if mm_corto < mm_largo and mm_mediano < mm_largo and mm_corto < mm_mediano and self.crypto_balance > 0:
            # Vender el 100% del saldo en cripto
            valor_venta = self.crypto_balance * precio_actual
            self.budget += valor_venta
            cantidad_vendida = self.crypto_balance
            self.last_action = 'sell'
            self.crypto_balance = 0
            self.registrar_operacion("Venta (100%)", precio_actual, cantidad_vendida)
            return

        if mm_mediano < mm_largo and mm_mediano_prev > mm_largo_prev and self.crypto_balance > 0:
            # Vender el 100% del saldo en cripto
            valor_venta = self.crypto_balance * precio_actual
            self.budget += valor_venta
            cantidad_vendida = self.crypto_balance
            self.last_action = 'sell'
            self.crypto_balance = 0
            self.registrar_operacion("Venta (100%)", precio_actual, cantidad_vendida)
            return

        if (mm_corto > mm_largo 
            and mm_mediano > mm_largo # redundante
            and mm_corto < mm_mediano 
            and mm_mediano_prev > mm_largo_prev
            and self.crypto_balance > 0 
            and self.last_action != "sell-50"):
            # Vender el 50% del saldo en cripto
            cantidad_vendida = self.crypto_balance * 0.5
            valor_venta = cantidad_vendida * precio_actual
            self.budget += valor_venta
            self.last_action = "sell-50"
            self.crypto_balance *= 0.5
            self.registrar_operacion("Venta (50%)", precio_actual, cantidad_vendida)
            return


        # Incrementar la hora en simulación
        if self.current_time:
            self.current_time += timedelta(hours=1)

    def estado_actual(self):
        """Imprime el estado actual del bot."""
        print(f"Budget: {self.budget:.2f} USDT")
        print(f"Balance cripto: {self.crypto_balance:.6f} unidades")
        print(f"Última acción: {self.last_action}")

    def mostrar_historial(self):
        """Muestra el historial de operaciones como un DataFrame."""
        return pd.DataFrame(self.historial_operaciones)

    def graficar_rendimiento(self):
        """Genera un gráfico del rendimiento acumulado."""
        df = pd.DataFrame(self.historial_operaciones)
        if "Ganancia/Pérdida Acumulada" in df.columns:
            df["Ganancia/Pérdida Acumulada"].plot(kind="line", figsize=(10, 6))
            plt.title("Rendimiento Acumulado del Bot")
            plt.xlabel("Operación")
            plt.ylabel("Ganancia/Pérdida Acumulada (USDT)")
            plt.grid()
            plt.show()
        else:
            print("No hay suficientes datos para graficar el rendimiento.")