#!/usr/bin/env python3
"""
Script para analizar el archivo ICFES.xlsx y entender su estructura
para diseñar el modelo de tablas relacionales
"""

import pandas as pd
import os
import json


def analyze_icfes_excel():
    """Analiza el archivo ICFES.xlsx y muestra su estructura"""
    
    # Ajustar ruta para el contenedor
    excel_path = "../Icfes/ICFES.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ Archivo no encontrado: {excel_path}")
        # Intentar rutas alternativas
        alt_paths = [
            "/app/../Icfes/ICFES.xlsx",
            "/Icfes/ICFES.xlsx", 
            "Icfes/ICFES.xlsx",
            "../Icfes/ICFES.xlsx"
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                excel_path = alt_path
                break
        else:
            print("Rutas alternativas probadas:")
            for alt_path in alt_paths:
                print(f"  {alt_path}: {'✅' if os.path.exists(alt_path) else '❌'}")
            return
    
    print("📊 Analizando archivo ICFES.xlsx...")
    print(f"📁 Ruta: {excel_path}")
    print("=" * 60)
    
    try:
        # Leer el archivo Excel - obtener todas las hojas
        excel_file = pd.ExcelFile(excel_path)
        print(f"📋 Hojas encontradas: {excel_file.sheet_names}")
        print("=" * 60)
        
        # Analizar cada hoja
        for sheet_name in excel_file.sheet_names:
            print(f"\n📄 HOJA: {sheet_name}")
            print("-" * 40)
            
            # Leer la hoja
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"📊 Columnas: {list(df.columns)}")
            
            # Mostrar tipos de datos
            print("\n🔍 Tipos de datos:")
            for col in df.columns:
                dtype = df[col].dtype
                non_null = df[col].notna().sum()
                null_count = df[col].isna().sum()
                print(f"  {col}: {dtype} ({non_null} no nulos, {null_count} nulos)")
            
            # Mostrar las primeras filas
            print(f"\n📋 Primeras 5 filas:")
            print(df.head().to_string())
            
            # Estadísticas básicas para columnas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\n📈 Estadísticas de columnas numéricas:")
                print(df[numeric_cols].describe().to_string())
            
            # Valores únicos para columnas categóricas
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 20:  # Solo mostrar si hay pocos valores únicos
                    print(f"\n🏷️ Valores únicos en '{col}': {list(unique_values)}")
                else:
                    print(f"\n🏷️ '{col}' tiene {len(unique_values)} valores únicos")
            
            print("\n" + "=" * 60)
        
        # Guardar resumen en JSON para análisis posterior
        summary = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            summary[sheet_name] = {
                'dimensions': {
                    'rows': int(df.shape[0]),
                    'columns': int(df.shape[1])
                },
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'sample_data': df.head(3).to_dict('records')
            }
        
        # Guardar resumen
        with open('icfes_excel_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print("✅ Análisis completado!")
        print("📄 Resumen guardado en: icfes_excel_analysis.json")
        
    except Exception as e:
        print(f"❌ Error al analizar el archivo: {str(e)}")
        print("💡 Asegúrate de tener pandas y openpyxl instalados:")
        print("   pip install pandas openpyxl")


if __name__ == "__main__":
    analyze_icfes_excel() 