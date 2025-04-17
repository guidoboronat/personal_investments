precios = [100, 102, 101, 104, 103, 105, 106, 107, 106, 108, 110, 109, 111, 112]


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



