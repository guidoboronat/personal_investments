# Personal Investments
La idea de este repositorio es desarrollar distintas estrategias de trading automatico. Dicho esto el repositorio estara conformado por los siguientes modulos:
- Integracion_API_binance: definimos funciones para consumir precios en distintas temporalidade y para realizar operaciones.
- Estrategia: aqui vamos a definir distintos tipos de estrategias, desde cruce de medias moviles hasta representacion de los resultados a traves de modelos exponenciales.

## Integracion Binance
### Obtencion de precios
- url = "https://api.binance.com/api/v3/klines"

Este endpoint acepta los siguientes parametros:
- symbol: "BTCUSDT"
- interval: "1h"
- startTime: timestamp
- endTime: timestamp
- limit: Binance tiene un maximo de 1000.

Response (JSON):
Cada vela (`kline`) se representa como una lista con los siguientes campos:

| Índice | Campo                          | Descripción                                                                 |
|--------|--------------------------------|-----------------------------------------------------------------------------|
| 0      | Open time                      | Hora de apertura (timestamp en milisegundos desde Epoch)                   |
| 1      | Open price                     | Precio de apertura                                                         |
| 2      | High price                     | Precio máximo alcanzado durante el intervalo                               |
| 3      | Low price                      | Precio mínimo alcanzado durante el intervalo                               |
| 4      | Close price                    | Precio de cierre                                                           |
| 5      | Volume                         | Volumen operado del activo base (por ejemplo, BTC)                         |
| 6      | Close time                     | Hora de cierre (timestamp en milisegundos desde Epoch)                     |
| 7      | Quote asset volume             | Volumen operado del activo cotizado (por ejemplo, USDT)                    |
| 8      | Number of trades               | Cantidad de operaciones realizadas durante la vela                         |
| 9      | Taker buy base asset volume    | Volumen comprado por takers (en activo base, ej. BTC)                      |
| 10     | Taker buy quote asset volume   | Volumen comprado por tak


## Estrategias
...


