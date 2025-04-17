import requests
import time
from collections import deque
from datetime import datetime,timedelta
import pandas as pd
import matplotlib.pyplot as plt

def get_token_price(symbol):
    # Endpoint de la API para obtener precios
    url = f"https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}  # El símbolo debe estar en mayúsculas (e.g., BTCUSDT)
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza un error si la respuesta no es exitosa
        data = response.json()
        price = data['price']  # El precio del token
        return float(price)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el precio: {e}")
        return None


class MediaMovil:
    def __init__(self, periodos):
        self.periodos = periodos
        self.precios = deque(maxlen=periodos)  # Lista fija con tamaño máximo
        self.suma = 0  # Acumulador de la suma de precios
        

    def agregar_precio(self, precio):
        if len(self.precios) == self.periodos:
            # Si la lista está llena, resta el valor más antiguo
            self.suma -= self.precios[0]
        # Agrega el nuevo precio y actualiza la suma
        self.precios.append(precio)
        self.suma += precio

    def calcular_mm(self):
        # Calcula la media móvil solo si hay suficientes datos
        if len(self.precios) < self.periodos:
            return None  # No hay suficientes datos para calcular
        return self.suma / self.periodos

class Mark1:
    def __init__(self, budget,corto,largo):
        self.budget = budget  # Capital inicial en USDT
        self.budget_inicial = budget
        self.corto = corto
        self.largo = largo
        self.crypto_balance = 0  # Cantidad de criptomonedas en posesión
        self.prices = deque(maxlen=largo)  # Mantiene un historial de hasta 25 precios
        self.last_action = None  # Guarda la última acción: 'buy', 'sell' o None
        self.ganancia_perdida_acumulada = 0  # Ganancia/Pérdida total acumulada
        self.rendimiento_porcentaje = 0
        self.historial_operaciones = []  # Registro de operaciones
        self.precio_compra = None  # Precio al que se realizó la última compra

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
        mm_corto = self.calcular_media_movil(int(self.corto))
        mm_mediano = self.calcular_media_movil(int(self.largo))

        if mm_corto is None or mm_mediano is None:
            return  # No toma decisiones si no hay suficientes datos

        # Lógica de trading
        if mm_corto > mm_mediano and self.budget > 0 and self.last_action != 'buy':
            # Comprar todo el budget
            self.crypto_balance = self.budget / precio_actual
            self.precio_compra = precio_actual
            self.budget = 0
            self.last_action = 'buy'
            # print(f"Compra realizada: {self.crypto_balance:.6f} unidades a {precio_actual} USDT")
            self.registrar_operacion("Compra", precio_actual, self.crypto_balance)
        
        elif mm_corto < mm_mediano and self.crypto_balance > 0 and self.last_action != 'sell':
            # Vender todo
            valor_venta = self.crypto_balance * precio_actual
            ganancia_perdida = valor_venta - (self.precio_compra * self.crypto_balance)
            self.ganancia_perdida_acumulada += ganancia_perdida
            self.rendimiento_porcentaje = self.ganancia_perdida_acumulada/self.budget_inicial
            self.budget = valor_venta
            cantidad_vendida = self.crypto_balance
            self.crypto_balance = 0
            self.last_action = 'sell'
            # print(f"Venta realizada: {self.budget:.2f} USDT a {precio_actual} USDT")
            self.registrar_operacion("Venta", precio_actual, cantidad_vendida)

    def estado_actual(self):
        """Imprime el estado actual del bot."""
        print(f"Budget: {self.budget:.2f} USDT")
        # print(f"Balance cripto: {self.crypto_balance:.6f} unidades")
        # print(f"Última acción: {self.last_action}")

    def mostrar_historial(self):
        """Muestra el historial de operaciones como un DataFrame."""
        df = pd.DataFrame(self.historial_operaciones)
        print(df)
        return df

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


## INICIOS

# mm7 = MediaMovil(periodos=7) esto es utilizando la clase medias moviles
# mm25 = MediaMovil(periodos=25)

if __name__ == "__main__":
    symbol = "BTCUSDT"  # Cambia esto por el token que quieras
    bot = Mark1(budget=1000)

    while True:
        precio = get_token_price(symbol)
        if precio is not None:
            print("Precio actual: ",precio)
            print("Media movil 7: ",bot.calcular_media_movil(periodos=7))
            print("Media movil 25: ",bot.calcular_media_movil(periodos=25))
            bot.agregar_precio(precio)
            bot.tomar_decision(precio)
            bot.estado_actual()
        time.sleep(60)  # Actualiza cada 5 segundos


