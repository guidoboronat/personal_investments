#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico del problema con COPY en PostgreSQL
"""

import pandas as pd
import os
from binance import obtener_precios_historicos

def diagnosticar_problema():
    print("=== DIAGNÓSTICO DEL PROBLEMA CON COPY ===")
    
    # 1. Obtener datos de Binance
    try:
        print("1. Obteniendo datos de Binance...")
        df = pd.DataFrame(obtener_precios_historicos("BTCUSDT", "1h", "2024-01-01", "2024-01-05"))
        print(f"   ✅ DataFrame creado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"   Columnas: {list(df.columns)}")
        print(f"   Tipos de datos:")
        for col, dtype in df.dtypes.items():
            print(f"     - {col}: {dtype}")
    except Exception as e:
        print(f"   ❌ ERROR obteniendo datos: {e}")
        return
    
    # 2. Verificar CSV con headers
    csv_path = "/Users/guidoboronat/personal/repo trading/personal_investments/personal_investments-1/Trading/Precios BTC/temp_btc_prices.csv"
    
    print("\n2. Probando CSV con headers (header=True)...")
    df.to_csv(csv_path, index=False, header=True)
    
    if os.path.exists(csv_path):
        print(f"   ✅ CSV creado en: {csv_path}")
        with open(csv_path, 'r') as f:
            lines = f.readlines()[:3]
        print(f"   Primeras líneas del CSV:")
        for i, line in enumerate(lines):
            print(f"   Línea {i+1}: {line.strip()}")
    else:
        print(f"   ❌ ERROR: No se pudo crear el CSV")
        return
    
    # 3. Verificar CSV sin headers
    print("\n3. Probando CSV sin headers (header=False)...")
    csv_path_no_header = "/Users/guidoboronat/personal/repo trading/personal_investments/personal_investments-1/Trading/Precios BTC/temp_btc_prices_no_header.csv"
    df.to_csv(csv_path_no_header, index=False, header=False)
    
    if os.path.exists(csv_path_no_header):
        print(f"   ✅ CSV sin headers creado en: {csv_path_no_header}")
        with open(csv_path_no_header, 'r') as f:
            lines = f.readlines()[:3]
        print(f"   Primeras líneas del CSV (sin headers):")
        for i, line in enumerate(lines):
            print(f"   Línea {i+1}: {line.strip()}")
    else:
        print(f"   ❌ ERROR: No se pudo crear el CSV sin headers")
    
    # 4. Verificar estructura de datos problemática
    print("\n4. Verificando datos problemáticos...")
    print(f"   Valores nulos: {df.isnull().sum().sum()}")
    print(f"   Valores infinitos: {df.isin([float('inf'), float('-inf')]).sum().sum()}")
    
    # Verificar columnas con problemas potenciales
    for col in df.columns:
        if df[col].dtype == 'object':
            print(f"   ⚠️  Columna '{col}' es tipo object - podría causar problemas")
        if df[col].isnull().any():
            print(f"   ⚠️  Columna '{col}' tiene valores nulos")
    
    # 5. Limpiar archivos temporales
    print("\n5. Limpiando archivos temporales...")
    for temp_file in [csv_path, csv_path_no_header]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"   🗑️  Eliminado: {temp_file}")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")
    print("\nPOSIBLES SOLUCIONES:")
    print("1. Usar header=False en df.to_csv()")
    print("2. Verificar que la tabla btc_prices_1h existe en PostgreSQL")
    print("3. Verificar que los tipos de datos coinciden entre CSV y tabla")
    print("4. Verificar la conexión a la base de datos")

if __name__ == "__main__":
    diagnosticar_problema() 