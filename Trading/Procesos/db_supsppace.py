import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from binance import obtener_precios_historicos
import pandas as pd
import os

# Load environment variables from .env
class PostgresDB:
    def __init__(self, dotenv_path):
        # Cargar variables de entorno
        load_dotenv(dotenv_path)
        self.user = os.getenv("user")
        self.password = os.getenv("password")
        self.host = os.getenv("host")
        self.port = os.getenv("port")
        self.dbname = os.getenv("dbname")
        try:
            self.conn = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.dbname
            )
            self.cursor = self.conn.cursor()
            print("✅ Conexión exitosa a PostgreSQL")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def execute(self, query, params=None):
        """Ejecuta una query (INSERT, UPDATE, DELETE, DDL)."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error al ejecutar la query: {e}")

    def fetchall(self, query, params=None):
        """Ejecuta una consulta SELECT y devuelve todos los resultados."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
            return []

    def get_table_info(self, table_name):
        """Devuelve información de las columnas de una tabla."""
        try:
            self.cursor.execute(
                sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;"),
                [table_name]
            )
            columns = self.cursor.fetchall()
            print(f"📋 Estructura de la tabla '{table_name}':")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            return columns
        except Exception as e:
            print(f"❌ Error al obtener información de la tabla '{table_name}': {e}")
            return []
        
    def insert_dataframe(self, df, table_name):
        """Inserta un DataFrame en la tabla especificada."""
        for index, row in df.iterrows():
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            values = tuple(row.values)
            self.execute(query, values)
        print(f"✅ Insertados {len(df)} registros en la tabla '{table_name}'")

    def copy_from_csv(self, csv_path, table_name, columns=None):
        """Carga datos desde un CSV usando COPY (muy rápido para PostgreSQL)."""
        try:
            with open(csv_path, 'r') as file:
                self.cursor.copy_from(
                    file, 
                    table_name, 
                    sep=',', 
                    columns=columns  # Lista de nombres de columnas en el orden del CSV
                )
            self.conn.commit()
            print(f"✅ Datos cargados exitosamente desde {csv_path} a {table_name}")
            
        except Exception as e:
            print(f"❌ Error en COPY: {e}")
            self.conn.rollback()
        
        finally:
            # Limpiar archivo temporal
            import os
            if os.path.exists(csv_path):
                os.remove(csv_path)
                print(f"��️  Archivo temporal {csv_path} eliminado")

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        self.cursor.close()
        self.conn.close()
        print("Conexión cerrada.")



df = pd.DataFrame(obtener_precios_historicos("BTCUSDT", "1h", "2024-01-01", "2024-12-31"))

print(df.head())



# 2. Guardar a CSV
csv_path = "temp_btc_prices.csv"
df.to_csv(csv_path, index=False, header=False)

dao = PostgresDB("/Users/guidoboronat/personal/repo trading/personal_investments/secrte.env")
# 3. Cargar con COPY
columns = ['symbol', 'interval', 'open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'close_time', 'quote_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote']
dao.copy_from_csv(csv_path, "btc_prices_1h", columns)
dao.cerrar()

