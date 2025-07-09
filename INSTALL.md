# 🚀 Guía de Instalación - ICFES AI Tutor

Esta guía te ayudará a instalar y configurar el sistema ICFES AI Tutor en tu entorno local.

## 📋 Prerrequisitos

Asegúrate de tener instalados los siguientes programas:

### Software Requerido

1. **Python 3.8 o superior**
   - Descargar desde: https://www.python.org/downloads/
   - Verificar instalación: `python --version`

2. **Node.js 18 o superior**
   - Descargar desde: https://nodejs.org/
   - Verificar instalación: `node --version`

3. **Git**
   - Descargar desde: https://git-scm.com/
   - Verificar instalación: `git --version`

### Software Opcional (Recomendado)

- **Visual Studio Code**: Editor de código recomendado
- **Postman**: Para probar la API
- **DB Browser for SQLite**: Para visualizar la base de datos

## 🎯 Instalación Rápida (Recomendada)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/icfes-ai-tutor.git
cd icfes-ai-tutor
```

### Paso 2: Ejecutar Instalación Automática

```bash
python setup.py
```

El script automático se encargará de:
- ✅ Verificar prerrequisitos del sistema
- ✅ Crear entorno virtual de Python
- ✅ Instalar dependencias de Python
- ✅ Instalar dependencias de Node.js
- ✅ Crear archivos de configuración
- ✅ Inicializar la base de datos
- ✅ Crear scripts de inicio

### Paso 3: Iniciar la Aplicación

**En Windows:**
```bash
# Terminal 1 - Backend
start_backend.bat

# Terminal 2 - Frontend
start_frontend.bat
```

**En Linux/Mac:**
```bash
# Terminal 1 - Backend
./start_backend.sh

# Terminal 2 - Frontend
./start_frontend.sh
```

### Paso 4: Verificar Instalación

- Abrir http://localhost:3000 en tu navegador
- Iniciar sesión con: `admin@icfes.com` / `admin123`

---

## 🔧 Instalación Manual (Avanzada)

Si prefieres instalar manualmente o el script automático no funciona:

### 1. Entorno Virtual de Python

```bash
# Crear entorno virtual
python -m venv venv-all

# Activar entorno virtual
# Windows:
venv-all\Scripts\activate
# Linux/Mac:
source venv-all/bin/activate
```

### 2. Dependencias de Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Dependencias del Frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Configuración de Entorno

#### Backend (`backend/.env`)

```env
DATABASE_URL=sqlite:///./icfes_tutor.db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
ENVIRONMENT=development
```

#### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### 5. Inicializar Base de Datos

```bash
cd backend
python app/core/init_db.py
cd ..
```

### 6. Iniciar Servidores

```bash
# Terminal 1 - Backend
cd backend
source ../venv-all/bin/activate  # Linux/Mac
# o venv-all\Scripts\activate    # Windows
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🛠️ Configuración Avanzada

### Variables de Entorno Opcionales

#### OpenAI Integration
```env
OPENAI_API_KEY=your-openai-api-key-here
```

#### Redis (Para producción)
```env
REDIS_URL=redis://localhost:6379
```

#### Email (Para notificaciones)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Base de Datos Alternativa (PostgreSQL)

```env
DATABASE_URL=postgresql://user:password@localhost/icfes_tutor
```

## 🔍 Verificación de la Instalación

### 1. Verificar Backend

```bash
curl http://127.0.0.1:8000/health
```

Debería devolver: `{"status": "healthy"}`

### 2. Verificar Frontend

- Navegar a http://localhost:3000
- Debería aparecer la página de login

### 3. Verificar API Documentation

- Navegar a http://127.0.0.1:8000/docs
- Debería aparecer la documentación de Swagger

### 4. Verificar Base de Datos

```bash
# Desde el directorio backend
python -c "from app.core.database import engine; print('DB Connected!' if engine else 'DB Error')"
```

## 🐛 Solución de Problemas

### Problema: "Python no encontrado"

```bash
# Verificar instalación de Python
python --version
# o
python3 --version

# Si no está instalado, descargar desde python.org
```

### Problema: "Node no encontrado"

```bash
# Verificar instalación de Node.js
node --version

# Si no está instalado, descargar desde nodejs.org
```

### Problema: "Puerto 8000 en uso"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Problema: "Port 3000 en uso"

```bash
# Cambiar puerto en frontend
cd frontend
npm run dev -- -p 3001
```

### Problema: "Dependencias no instaladas"

```bash
# Limpiar cache de npm
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Reinstalar dependencias de Python
pip install --force-reinstall -r requirements.txt
```

### Problema: "Base de datos no inicializada"

```bash
cd backend
rm -f icfes_tutor.db  # Eliminar BD existente
python app/core/init_db.py  # Recrear BD
```

## 📊 Monitoreo del Sistema

### Logs del Backend

```bash
# Ver logs en tiempo real
cd backend
tail -f uvicorn.log
```

### Logs del Frontend

```bash
# Los logs aparecen en la consola donde ejecutaste npm run dev
cd frontend
npm run dev
```

### Verificar Procesos

```bash
# Windows
tasklist | findstr python
tasklist | findstr node

# Linux/Mac
ps aux | grep python
ps aux | grep node
```

## 🎓 Siguientes Pasos

Una vez instalado correctamente:

1. **Explorar la aplicación** con las credenciales de prueba
2. **Leer la documentación** en `/docs`
3. **Configurar OpenAI** para funciones de IA (opcional)
4. **Personalizar configuración** según tus necesidades
5. **Revisar el código** para entender la arquitectura

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. Revisar esta guía completa
2. Buscar en [GitHub Issues](https://github.com/tu-usuario/icfes-ai-tutor/issues)
3. Crear un nuevo issue con detalles del problema
4. Incluir logs y versiones de software

---

**¡Listo para empezar a usar ICFES AI Tutor! 🎉** 