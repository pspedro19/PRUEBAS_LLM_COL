# 📁 Scripts del Proyecto ICFES-LLM

Esta carpeta contiene todos los scripts Python organizados por categorías para mantener el proyecto limpio y organizado.

## 📂 Estructura de Carpetas

```
scripts/
├── README.md                    # Este archivo
├── setup.sh                     # Script de configuración inicial
├── database_scripts/            # Scripts de base de datos y análisis
├── test_scripts/               # Scripts de pruebas y validación
└── ai_scripts/                 # Scripts relacionados con AI/LLM
```

## 📊 Database Scripts

Scripts para análisis y gestión de la base de datos:

### 📋 Análisis de Tablas
- `show_all_tables_complete.py` - Información completa de todas las tablas
- `simple_table_info.py` - Información simplificada de tablas
- `quick_table_info.py` - Información rápida de tablas
- `detailed_table_info.py` - Información detallada con claves
- `detailed_table_info_fixed.py` - Versión corregida del script detallado

### 🔍 Verificación de Integridad
- `verify_ai_foreign_keys.py` - Verificación específica de Foreign Keys AI
- `check_foreign_keys.py` - Verificación general de Foreign Keys
- `complete_system_verification.py` - Verificación completa del sistema

### 📈 Análisis de Datos
- `generate_db_diagram.py` - Generación de diagramas ASCII de BD
- `simple_db_overview.py` - Vista general simplificada
- `detailed_ascii_diagram.py` - Diagramas ASCII detallados

### 🎯 Análisis de Preparación
- `llm_integration_analysis.py` - Análisis de preparación para LLM
- `exhaustive_system_review.py` - Revisión exhaustiva del sistema
- `critical_features_verification.py` - Verificación de características críticas
- `final_api_verification.py` - Verificación final de APIs

## 🧪 Test Scripts

Scripts para pruebas y validación:

### 🔄 Pruebas de Flujo
- `test_progress.py` - Prueba del flujo de progreso
- `test_images.py` - Prueba de imágenes
- `test_specific_images.py` - Prueba de imágenes específicas

### 📊 Pruebas de APIs
- `test_ai_apis.py` - Pruebas de APIs AI
- `test_progress.py` - Pruebas de progreso

### ✅ Verificación de Datos
- `verify_ai_tables.py` - Verificación de tablas AI
- `create_ai_data.py` - Creación de datos de prueba AI

## 🤖 AI Scripts

Scripts relacionados con AI/LLM:

### 🔍 Verificación AI
- `check_ai_tables.py` - Verificación específica de tablas AI
- `verify_ai_foreign_keys.py` - Verificación de Foreign Keys AI

### 📊 Análisis AI
- `llm_integration_analysis.py` - Análisis de integración LLM
- `create_ai_data.py` - Creación de datos AI

## 🚀 Cómo Usar

### Para Scripts de Base de Datos:
```bash
# Copiar al contenedor
docker cp scripts/database_scripts/nombre_script.py mathquest-backend:/app/

# Ejecutar
docker-compose exec backend python nombre_script.py
```

### Para Scripts de Pruebas:
```bash
# Copiar al contenedor
docker cp scripts/test_scripts/nombre_script.py mathquest-backend:/app/

# Ejecutar
docker-compose exec backend python nombre_script.py
```

### Para Scripts AI:
```bash
# Copiar al contenedor
docker cp scripts/ai_scripts/nombre_script.py mathquest-backend:/app/

# Ejecutar
docker-compose exec backend python nombre_script.py
```

## 📝 Notas Importantes

1. **Todos los scripts requieren Django configurado**
2. **Algunos scripts modifican la base de datos**
3. **Siempre hacer backup antes de ejecutar scripts de modificación**
4. **Los scripts están diseñados para el entorno Docker**

## 🔧 Scripts Principales

### Para Verificación Rápida:
```bash
# Verificar estado general
docker cp scripts/database_scripts/quick_table_info.py mathquest-backend:/app/
docker-compose exec backend python quick_table_info.py

# Verificar tablas AI
docker cp scripts/ai_scripts/check_ai_tables.py mathquest-backend:/app/
docker-compose exec backend python check_ai_tables.py
```

### Para Análisis Completo:
```bash
# Análisis completo del sistema
docker cp scripts/database_scripts/complete_system_verification.py mathquest-backend:/app/
docker-compose exec backend python complete_system_verification.py
```

## 📊 Estado del Proyecto

- ✅ **98 tablas creadas**
- ✅ **149 Foreign Keys configuradas**
- ✅ **485 índices optimizados**
- ✅ **Sistema listo para producción**
- ✅ **Integración LLM preparada**

---

**🎯 El proyecto está 100% funcional y organizado!** 