from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

class Mark1:
    def __init__(self, budget,corto,largo):
        self.budget = budget  # Capital inicial en USDT
        self.budget_inicial = budget
        self.corto = corto
        self.largo = largo
        self.crypto_balance = 0  # Cantidad de criptomonedas en posesión
        self.prices = deque(maxlen=largo)  # Mantiene un historial de hasta 25 precios
        self.mm_corto_list = deque(maxlen=2)
        self.mm_largo_list = deque(maxlen=2)
        self.last_action = None  # Guarda la última acción: 'buy', 'sell' o None
        self.ganancia_perdida_acumulada = 0  # Ganancia/Pérdida total acumulada
        self.rendimiento_porcentaje = 0
        self.historial_operaciones = []  # Registro de operaciones
        self.precio_compra = None  # Precio al que se realizó la última compra

    def agregar_precio(self, precio):
        """Funcion para agregar el ultimo precio a la lista de precios, la cual tiene un tope
        segun el dato largo"""
        self.prices.append(precio)

    def calcular_media_movil(self, periodos):
        """Calcula la media móvil para los últimos 'periodos' precios.
        Parametros:
        Peridos, sobre los cuales se calculara la media
        
        Response:
        Si la cantidad de precios almacenados no son suficientes para calcular la media, devuelve None"""
        if len(self.prices) < periodos:
            return None  # No hay suficientes datos para calcular la media móvil
        mm = sum(list(self.prices)[-periodos:]) / periodos
        return mm

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
        self.mm_corto_list.append(mm_corto)
        mm_largo = self.calcular_media_movil(int(self.largo))
        self.mm_largo_list.append(mm_largo)


        mm_corto_prev = self.mm_corto_list[-2]
        mm_largo_prev = self.mm_largo_list[-2]

        if mm_corto_prev is None or mm_largo_prev is None:
            return  # No toma decisiones si no hay suficientes datos

        elif self.last_action == 'buy' and self.crypto_balance > 0 and mm_corto_prev > mm_largo_prev:
            if mm_corto < mm_largo:
                # Vender todo
                valor_venta = self.crypto_balance * precio_actual
                ganancia_perdida = valor_venta - (self.precio_compra * self.crypto_balance) # calculamos contra ultima compra
                self.ganancia_perdida_acumulada += ganancia_perdida
                self.rendimiento_porcentaje = self.ganancia_perdida_acumulada/self.budget_inicial
                self.budget = valor_venta
                cantidad_vendida = self.crypto_balance
                self.crypto_balance = 0
                self.last_action = 'sell'
                # print(f"Venta realizada: {self.budget:.2f} USDT a {precio_actual} USDT")
                self.registrar_operacion("Venta", precio_actual, cantidad_vendida)
            else:
                print(f"No se ejecuta venta, mm_corto: {mm_corto} sige por arriba de mm_largo: {mm_largo}")


        # Lógica de trading
        if self.budget > 0 and mm_corto_prev < mm_largo_prev:
            if mm_corto > mm_largo:
                # Comprar todo el budget
                self.crypto_balance = self.budget / precio_actual
                self.precio_compra = precio_actual
                self.budget = 0
                self.last_action = 'buy'
                print(f"Compra realizada: {self.crypto_balance:.6f} unidades a {precio_actual} USDT")
                self.registrar_operacion("Compra", precio_actual, self.crypto_balance)
                return
            else:
                print(f"No se ejecuta compra, mm_corto: {mm_corto} sigue debajo de mm_largo: {mm_largo}")
        

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
        if "Ganancia/Pérdida Acumulada" in df.columns:
            df["Ganancia/Pérdida Acumulada"].plot(kind="line", figsize=(10, 6))
            plt.title("Rendimiento Acumulado del Bot")
            plt.xlabel("Operación")
            plt.ylabel("Ganancia/Pérdida Acumulada (USDT)")
            plt.grid()
            plt.show()
        else:
            print("No hay suficientes datos para graficar el rendimiento.")


