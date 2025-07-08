#!/bin/bash

# ICFES AI Tutor - Setup Script
echo "🚀 Configurando ICFES AI Tutor..."

# Crear directorios si no existen
echo "📁 Creando estructura de directorios..."
mkdir -p backend/app/{api/endpoints,core,models,services,utils} backend/alembic database frontend/src/{app,components/ui,lib,hooks} frontend/public scripts

# Configurar backend
echo "🐍 Configurando backend..."
cd backend

# Instalar dependencias de Python (opcional si no se usa Docker)
if command -v python3 &> /dev/null; then
    echo "Creando entorno virtual de Python..."
    python3 -m venv venv
    
    # Activar entorno virtual según el sistema operativo
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    echo "Instalando dependencias de Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

cd ..

# Configurar frontend
echo "🌐 Configurando frontend..."
cd frontend

# Instalar dependencias de Node.js
if command -v npm &> /dev/null; then
    echo "Instalando dependencias de Node.js..."
    npm install
else
    echo "⚠️  npm no encontrado. Por favor instala Node.js para continuar."
fi

cd ..

# Crear archivos de configuración adicionales
echo "⚙️  Creando archivos de configuración..."

# Crear tsconfig.json para frontend
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Crear postcss.config.js
cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Crear .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
venv/
__pycache__/

# Build outputs
.next/
dist/
build/

# Environment variables
.env.local
.env.production

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Temporary files
*.tmp
*.temp
EOF

# Crear script de desarrollo
cat > start-dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando ICFES AI Tutor en modo desarrollo..."

# Función para manejar Ctrl+C
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Verificar si Docker está disponible
if command -v docker-compose &> /dev/null; then
    echo "🐳 Usando Docker Compose..."
    docker-compose up --build
else
    echo "💻 Usando modo desarrollo local..."
    
    # Iniciar backend
    echo "🐍 Iniciando backend..."
    cd backend
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    cd ..
    
    # Iniciar frontend
    echo "🌐 Iniciando frontend..."
    cd frontend
    npm run dev &
    cd ..
    
    echo "✅ Servicios iniciados:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   Documentación API: http://localhost:8000/docs"
    echo ""
    echo "Presiona Ctrl+C para detener todos los servicios"
    
    # Esperar a que termine
    wait
fi
EOF

chmod +x start-dev.sh

# Crear script de producción
cat > start-prod.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando ICFES AI Tutor en modo producción..."

if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.yml up -d
    echo "✅ Servicios iniciados en modo producción"
    echo "   Aplicación: http://localhost:3000"
    echo "   API: http://localhost:8000"
else
    echo "❌ Docker Compose requerido para modo producción"
    exit 1
fi
EOF

chmod +x start-prod.sh

# Crear README con instrucciones específicas
cat > SETUP.md << 'EOF'
# ICFES AI Tutor - Guía de Configuración

## 🚀 Instalación Rápida

### Opción 1: Con Docker (Recomendado)
1. Instala Docker y Docker Compose
2. Configura variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus API keys
   ```
3. Inicia la aplicación:
   ```bash
   ./start-prod.sh
   ```

### Opción 2: Sin Docker (Desarrollo)
1. **Requisitos previos:**
   - Python 3.11+
   - Node.js 18+
   - PostgreSQL 15+
   - Redis

2. **Configuración automática:**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configurar base de datos:**
   ```bash
   # Crear base de datos PostgreSQL
   createdb icfes_db
   
   # Ejecutar migraciones
   cd backend
   alembic upgrade head
   ```

4. **Iniciar servicios:**
   ```bash
   ./start-dev.sh
   ```

## 🔧 Configuración de API Keys

### OpenAI API Key
1. Ve a https://platform.openai.com/
2. Crea una API Key
3. Agrégala a `.env`:
   ```
   OPENAI_API_KEY=sk-tu-api-key-aqui
   ```

### Google OAuth
1. Ve a Google Cloud Console
2. Crea credenciales OAuth2
3. Agrégalas a `.env`:
   ```
   GOOGLE_CLIENT_ID=tu-client-id
   GOOGLE_CLIENT_SECRET=tu-client-secret
   ```

## 📱 Acceso a la Aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050 (solo Docker)

## 🛠️ Comandos Útiles

```bash
# Desarrollo
./start-dev.sh

# Producción
./start-prod.sh

# Detener servicios Docker
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar base de datos
docker-compose down -v
docker-compose up -d postgres
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
- Verifica que PostgreSQL esté ejecutándose
- Revisa las credenciales en `.env`

### Error de API OpenAI
- Verifica que tu API Key sea válida
- Revisa que tengas créditos disponibles

### Puerto ocupado
- Cambia los puertos en `docker-compose.yml`
- O detén los servicios que usen los puertos 3000/8000

## 📊 Estructura del Proyecto

```
Icfes_Pipeline/
├── backend/          # FastAPI + PostgreSQL
├── frontend/         # Next.js + Tailwind
├── database/         # Scripts de DB
├── scripts/          # Scripts de setup
├── docker-compose.yml
└── .env
```
EOF

echo ""
echo "✅ Setup completado exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura tus API keys en el archivo .env"
echo "2. Para desarrollo: ./start-dev.sh"
echo "3. Para producción: ./start-prod.sh"
echo ""
echo "📖 Lee SETUP.md para instrucciones detalladas"
echo ""
echo "🎯 Objetivo del MVP:"
echo "   - Sistema de autenticación ✓"
echo "   - Preguntas ICFES ✓"
echo "   - Razonamiento en cadena con IA ✓"
echo "   - Métricas por usuario ✓"
echo "   - Evaluación adaptativa (IRT) ✓"
echo ""
echo "🚀 ¡Tu plataforma ICFES AI está lista!" 