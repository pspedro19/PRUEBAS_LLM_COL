# 🎓 ICFES AI Tutor

**Sistema de Tutoría Inteligente para Pruebas ICFES Saber 11**

Una aplicación web completa que utiliza inteligencia artificial para proporcionar tutorías personalizadas y análisis avanzado basado en la Teoría de Respuesta al Ítem (IRT) para estudiantes que se preparan para las pruebas ICFES.

## 🌟 Características Principales

- **🤖 Tutor AI Inteligente**: Utiliza modelos de lenguaje avanzados para generar explicaciones personalizadas
- **📊 Análisis IRT**: Evaluación psicométrica avanzada del nivel de habilidad del estudiante
- **🎯 Recomendaciones Adaptativas**: Preguntas y temas sugeridos basados en el rendimiento individual
- **📈 Dashboard de Progreso**: Seguimiento detallado del avance académico
- **🔐 Sistema de Autenticación**: Gestión de usuarios con roles (estudiantes, tutores, administradores)
- **💾 Base de Datos SQLite**: Configuración simple y portable
- **🔄 API RESTful**: Backend modular con FastAPI
- **⚡ Frontend Moderno**: Interfaz responsiva con Next.js y Tailwind CSS

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido para Python
- **SQLAlchemy** - ORM para gestión de base de datos
- **SQLite** - Base de datos embebida
- **OpenAI/LangChain** - Integración con modelos de IA
- **NumPy/SciPy** - Computación científica para análisis IRT
- **Pandas** - Manipulación y análisis de datos
- **Pydantic** - Validación de datos y configuración
- **python-jose** - Manejo de tokens JWT
- **passlib** - Hashing seguro de contraseñas

### Frontend
- **Next.js 14** - Framework de React para producción
- **React 18** - Biblioteca para interfaces de usuario
- **Tailwind CSS** - Framework de CSS utilitario
- **TypeScript** - Tipado estático para JavaScript

## 🚀 Instalación Rápida

### Prerrequisitos
- **Python 3.8+** ([Descargar](https://www.python.org/downloads/))
- **Node.js 18+** ([Descargar](https://nodejs.org/))
- **Git** ([Descargar](https://git-scm.com/))

### Opción 1: Instalación Automática (Recomendada)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/icfes-ai-tutor.git
cd icfes-ai-tutor

# 2. Ejecutar instalación automática
python setup.py
```

### Opción 2: Instalación Manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/icfes-ai-tutor.git
cd icfes-ai-tutor

# 2. Crear entorno virtual de Python
python -m venv venv-all
# En Windows:
venv-all\Scripts\activate
# En Linux/Mac:
source venv-all/bin/activate

# 3. Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# 4. Instalar dependencias del frontend
cd frontend
npm install
cd ..

# 5. Configurar variables de entorno
# Copiar y editar los archivos .env de ejemplo
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 6. Inicializar base de datos
cd backend
python app/core/init_db.py
cd ..
```

## 🎮 Uso

### Iniciar la Aplicación

**Automático (Windows):**
```bash
# Terminal 1 - Backend
start_backend.bat

# Terminal 2 - Frontend  
start_frontend.bat
```

**Automático (Linux/Mac):**
```bash
# Terminal 1 - Backend
./start_backend.sh

# Terminal 2 - Frontend
./start_frontend.sh
```

**Manual:**
```bash
# Terminal 1 - Backend
cd backend
source ../venv-all/bin/activate  # Linux/Mac
# o venv-all\Scripts\activate  # Windows
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs

### Credenciales de Prueba

**Administrador:**
- Email: `admin@icfes.com`
- Contraseña: `admin123`

**Estudiante:**
- Email: `estudiante@ejemplo.com`
- Contraseña: `user123`

## 📁 Estructura del Proyecto

```
icfes-ai-tutor/
├── backend/                    # Servidor FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints de la API
│   │   ├── core/              # Configuración y seguridad
│   │   ├── models/            # Modelos de base de datos
│   │   ├── schemas/           # Esquemas Pydantic
│   │   └── services/          # Lógica de negocio
│   ├── .env                   # Variables de entorno del backend
│   └── requirements.txt       # Dependencias de Python
├── frontend/                  # Aplicación Next.js
│   ├── src/
│   │   ├── app/              # Páginas y layouts
│   │   └── components/       # Componentes reutilizables
│   ├── .env.local            # Variables de entorno del frontend
│   └── package.json          # Dependencias de Node.js
├── docs/                     # Documentación del proyecto
├── scripts/                  # Scripts de utilidad
├── setup.py                  # Script de instalación automática
├── requirements.txt          # Dependencias principales
└── README.md                 # Este archivo
```

## ⚙️ Configuración

### Variables de Entorno del Backend (`backend/.env`)

```env
# Base de datos
DATABASE_URL=sqlite:///./icfes_tutor.db

# Seguridad
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# OpenAI (opcional)
OPENAI_API_KEY=your-openai-api-key-here

# Entorno
ENVIRONMENT=development
```

### Variables de Entorno del Frontend (`frontend/.env.local`)

```env
# API del backend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Google OAuth (opcional)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## 📊 Funcionalidades Principales

### 1. Sistema de Autenticación
- Registro e inicio de sesión de usuarios
- Gestión de roles (estudiante, tutor, administrador)
- Tokens JWT para seguridad de sesiones

### 2. Evaluación Adaptativa
- Banco de preguntas categorizadas por área y dificultad
- Algoritmo IRT para selección de preguntas
- Estimación del nivel de habilidad θ (theta)

### 3. Tutor AI
- Explicaciones personalizadas generadas por IA
- Estrategias de resolución paso a paso
- Recomendaciones de estudio adaptativas

### 4. Analytics y Reportes
- Dashboard de progreso individual
- Análisis de fortalezas y debilidades
- Reportes de rendimiento por área

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Ejecutar tests del backend
cd backend
python -m pytest

# Linting y formato del código Python
black .
flake8 .
isort .

# Linting del frontend
cd frontend
npm run lint
npm run format

# Build de producción del frontend
npm run build
```

### Estructura de la Base de Datos

El sistema utiliza SQLite con las siguientes tablas principales:
- `users` - Información de usuarios
- `questions` - Banco de preguntas
- `responses` - Respuestas de estudiantes
- `sessions` - Sesiones de estudio
- `analytics` - Datos de análisis IRT

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/icfes-ai-tutor/wiki)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/icfes-ai-tutor/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/icfes-ai-tutor/discussions)

## 🙏 Agradecimientos

- [ICFES](https://www.icfes.gov.co/) por las especificaciones de las pruebas
- [OpenAI](https://openai.com/) por los modelos de lenguaje
- [FastAPI](https://fastapi.tiangolo.com/) por el excelente framework
- [Next.js](https://nextjs.org/) por el framework de frontend

---

**Desarrollado con ❤️ para mejorar la educación en Colombia** 