# Guía de Instalación - ICFES AI Tutor

## Requisitos Previos

### Para Desarrollo Local (sin Docker)
1. Python 3.11+ instalado
2. Node.js 18+ instalado
3. PostgreSQL 15+ instalado (opcional, puede usar SQLite para desarrollo)

### Para Docker (Opcional)
1. Docker Desktop
2. Docker Compose

## Instalación para Desarrollo Local

### Backend (Python)

1. Crear entorno virtual:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
# Copiar el archivo de ejemplo
cp backend/backend.env.example backend/backend.env

# Editar backend.env con tus credenciales
```

4. Inicializar la base de datos:
```bash
cd backend
alembic upgrade head
```

5. Ejecutar el servidor de desarrollo:
```bash
uvicorn app.api.main:app --reload
```

### Frontend (Next.js)

1. Instalar dependencias:
```bash
cd frontend
npm install
```

2. Configurar variables de entorno:
```bash
cp .env.example .env.local
# Editar .env.local con tus configuraciones
```

3. Ejecutar el servidor de desarrollo:
```bash
npm run dev
```

## Instalación con Docker (Opcional)

1. Construir y levantar los contenedores:
```bash
docker-compose up -d --build
```

2. La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Estructura del Proyecto

```
icfes-pipeline/
├── backend/                # Servidor FastAPI
│   ├── alembic/           # Migraciones de base de datos
│   ├── app/
│   │   ├── api/           # Endpoints y routers
│   │   ├── core/          # Configuración y DB
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── utils/         # Utilidades
│   └── tests/             # Tests unitarios y de integración
├── frontend/              # Cliente Next.js
│   ├── src/
│   │   ├── app/          # App router y páginas
│   │   ├── components/   # Componentes React
│   │   ├── hooks/        # Custom hooks
│   │   └── lib/          # Utilidades y configuración
│   └── public/           # Archivos estáticos
├── database/             # Scripts SQL y migraciones
├── scripts/             # Scripts de utilidad
└── docs/               # Documentación
```

## Configuración del IDE (Recomendado)

### VSCode
1. Instalar extensiones recomendadas:
   - Python
   - Pylance
   - ESLint
   - Prettier
   - Docker

2. Configurar formateo automático:
```json
{
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true
}
```

## Problemas Comunes

1. Error al activar el entorno virtual en Windows:
   - Ejecutar PowerShell como administrador
   - Ejecutar: `Set-ExecutionPolicy RemoteSigned`

2. Error de permisos en la base de datos:
   - Verificar las credenciales en backend.env
   - Asegurarse de que el usuario tiene permisos CREATE/ALTER

3. Error de módulos no encontrados:
   - Verificar que el entorno virtual está activado
   - Reinstalar dependencias: `pip install -r requirements.txt` 