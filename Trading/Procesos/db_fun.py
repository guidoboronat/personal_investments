import sqlite3

class daoDB:
    def __init__(self, db_path):
        """Inicializa la conexión a la base de datos."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"Conectado a la base de datos: {db_path}")

    def execute(self, query, params=None):
        """Ejecuta una query (INSERT, UPDATE, DELETE)."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al ejecutar la query: {e}")

    def fetchall(self, query, params=None):
        """Ejecuta una consulta SELECT y devuelve todos los resultados."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return []
        
    def insertar_klines(self, df):
        """
        Inserta un DataFrame de pandas en la tabla 'klines'.
        """
        query = """
        INSERT OR IGNORE INTO klines (
            symbol, interval, open_time, open_price, high_price, low_price,
            close_price, volume, close_time, quote_volume, num_trades,
            taker_buy_base, taker_buy_quote
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for row in df.iterrows():
            self.cursor.execute(query, (
                row["symbol"], row["interval"], row["open_time"], row["open_price"],
                row["high_price"], row["low_price"], row["close_price"], row["volume"],
                row["close_time"], row["quote_volume"], row["num_trades"],
                row["taker_buy_base"], row["taker_buy_quote"]
            ))
        self.conn.commit()

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()
        print("Conexión cerrada.")


