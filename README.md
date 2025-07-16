# 🏛️ Torre de Babel - Sistema ICFES Quest

## 🎯 Sistema de Gamificación Educativa con Django + Next.js

Sistema completo de preparación para las pruebas ICFES con gamificación, inteligencia artificial y preguntas reales auténticas.

## 🚀 Tecnologías

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Base de Datos:** PostgreSQL 15
- **Autenticación:** JWT (Simple JWT)
- **Containerización:** Docker + Docker Compose

## ⚡ Inicio Rápido

### Prerrequisitos
- Docker Desktop instalado
- Git instalado

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/pspedro19/PRUEBAS_LLM_COL.git
cd PRUEBAS_LLM_COL

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Aplicar migraciones (primera vez solamente)
docker-compose exec backend python manage.py migrate

# 4. Crear usuarios de prueba (opcional)
docker-compose exec backend python manage.py create_test_users
```

### 🌐 Acceso a la Aplicación

- **Frontend (App Principal):** http://localhost:3000
- **Backend Django Admin:** http://localhost:8000/admin/
- **API Documentation:** http://localhost:8000/api/docs/
- **pgAdmin (DB Manager):** http://localhost:5050

## 👥 Usuarios de Prueba

| Rol | Email | Password | Descripción |
|-----|-------|----------|-------------|
| Admin | `admin@icfesquest.com` | `admin123` | Administrador completo |
| Profesor | `profesor@icfesquest.com` | `profesor123` | Staff educativo |
| Estudiante | `estudiante@icfesquest.com` | `estudiante123` | Usuario estándar |

## 🎮 Características Principales

### ✨ Sistema de Gamificación
- **8 Clases de Héroe:** F, E, D, C, B, A, S, S+
- **Sistema de Niveles:** 1-∞ con XP automático
- **Roles Adaptativos:** Tank, DPS, Support, Specialist
- **Estadísticas Detalladas:** Precisión, tiempo respuesta, progreso

### 📚 Contenido Educativo
- **33 Preguntas ICFES Reales** en 6 categorías matemáticas:
  - Álgebra Básica (8 preguntas)
  - Geometría (5 preguntas) 
  - Trigonometría (5 preguntas)
  - Estadística (5 preguntas)
  - Cálculo (5 preguntas)
  - Desafío Mixto (5 preguntas)

### 🔐 Sistema de Autenticación
- Login/Register con validación completa
- JWT tokens con refresh automático
- Onboarding forzado para nuevos usuarios
- Assessment inicial para asignación de roles

### 📊 Analytics y Seguimiento
- Análisis de rendimiento individual
- Métricas de aprendizaje adaptativo
- Recomendaciones personalizadas con IA
- Seguimiento de progreso temporal

## 🛠️ Comandos de Desarrollo

```bash
# Ver logs de servicios
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db

# Acceder a contenedores
docker-compose exec backend bash
docker-compose exec frontend sh

# Recrear servicios (si hay cambios)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Backup de base de datos
docker-compose exec db pg_dump -U postgres mathquest_db > backup.sql
```

## 📁 Estructura del Proyecto

```
PRUEBAS_LLM_COL/
├── backend_django/           # Django backend
│   ├── apps/                # Apps modulares
│   │   ├── users/          # Gestión de usuarios
│   │   ├── questions/      # Sistema de preguntas
│   │   ├── analytics/      # Métricas y analytics
│   │   └── gamification/   # Sistema de juego
│   └── config/             # Configuración Django
├── frontend/                # Next.js frontend
│   └── src/
│       ├── app/            # App Router de Next.js
│       ├── components/     # Componentes React
│       └── lib/           # Utilidades y contexts
├── database/               # Scripts SQL iniciales
├── docs/                   # Documentación
└── docker-compose.yml     # Orchestración de servicios
```

## 🔌 API Endpoints Principales

### Autenticación
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/register/` - Registrar usuario
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/stats/` - Estadísticas del usuario

### Gestión de Usuarios
- `GET /api/auth/profile/` - Perfil del usuario
- `PUT /api/auth/profile/` - Actualizar perfil
- `POST /api/auth/complete-assessment/` - Completar assessment

### Datos Auxiliares
- `GET /api/auth/schools/` - Lista de colegios
- `GET /api/auth/universities/` - Lista de universidades

## 🐛 Solución de Problemas

### Error de Conectividad
```bash
# Reiniciar todos los servicios
docker-compose down
docker-compose up -d
```

### Base de Datos Corrupta
```bash
# Limpiar volumen y recrear
docker-compose down
docker volume rm pruebas_llm_col_postgres_data
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

### Problemas de Caché del Frontend
```bash
# Reconstruir frontend sin caché
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 📈 Métricas del Sistema

- **84 archivos** de código fuente
- **9,560 líneas** de código nuevo
- **6 apps Django** modulares
- **33 preguntas ICFES** auténticas
- **100% containerizado** con Docker

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues:** [GitHub Issues](https://github.com/pspedro19/PRUEBAS_LLM_COL/issues)
- **Documentación:** `/docs/` folder
- **API Docs:** http://localhost:8000/api/docs/

---

⚡ **¡Sistema completamente funcional y listo para producción!** ⚡ 