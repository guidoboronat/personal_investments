import sqlite3
import pandas as pd

class daoDB:
    def __init__(self, db_path):
        """Inicializa la conexión a la base de datos."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
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
        
        # Corregir el acceso a los datos del DataFrame
        for index, row in df.iterrows():
            self.cursor.execute(query, (
                row["symbol"], row["interval"], row["open_time"], row["open_price"],
                row["high_price"], row["low_price"], row["close_price"], row["volume"],
                row["close_time"], row["quote_volume"], row["num_trades"],
                row["taker_buy_base"], row["taker_buy_quote"]
            ))
        self.conn.commit()
        print(f"✅ Insertados {len(df)} registros en la tabla klines")

    def insert_dataframe(self, df, table_name, if_exists='append'):
        """
        Función genérica para insertar cualquier DataFrame en cualquier tabla.
        
        Args:
            df: DataFrame de pandas a insertar
            table_name: Nombre de la tabla destino
            if_exists: 'append' (insertar), 'replace' (reemplazar tabla), 'fail' (error si existe)

        A tener en cuenta:
        - Si los nombres de las columnas no coinciden con los de la tabla, lanzara un error.
        - Si los tipos de datos no coinciden con los de la tabla, lanzara un error.
        - Por eso tenemos la funcion get_table_info para obtener la estructura de la tabla.
        """
        try:
            # Usar pandas to_sql para inserción más eficiente
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
            print(f"✅ Insertados {len(df)} registros en la tabla '{table_name}'")
        except Exception as e:
            print(f"❌ Error al insertar en la tabla '{table_name}': {e}")

    def insert_dataframe_batch(self, df, table_name, batch_size=1000):
        """
        Inserta un DataFrame en lotes para mejor rendimiento con tablas grandes.
        
        Args:
            df: DataFrame de pandas a insertar
            table_name: Nombre de la tabla destino
            batch_size: Tamaño de cada lote
        """
        try:
            total_rows = len(df)
            inserted_rows = 0
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i + batch_size]
                batch.to_sql(table_name, self.conn, if_exists='append', index=False)
                inserted_rows += len(batch)
                print(f"📦 Lote insertado: {inserted_rows}/{total_rows} registros")
            
            print(f"✅ Completado: {inserted_rows} registros insertados en '{table_name}'")
        except Exception as e:
            print(f"❌ Error al insertar en la tabla '{table_name}': {e}")

    def get_table_info(self, table_name):
        """
        Obtiene información sobre la estructura de una tabla.
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            columns = self.fetchall(query)
            print(f"📋 Estructura de la tabla '{table_name}':")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            return columns
        except Exception as e:
            print(f"❌ Error al obtener información de la tabla '{table_name}': {e}")
            return []

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()
        print("Conexión cerrada.")


