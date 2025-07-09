#!/usr/bin/env python3
"""
ICFES AI Tutor Setup Script
Automated installation and configuration for the ICFES AI Tutor application
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path


class ICFESSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.venv_dir = self.root_dir / "venv-all"
        self.is_windows = platform.system() == "Windows"
        
    def run_command(self, command, cwd=None, check=True):
        """Execute shell command"""
        try:
            if isinstance(command, str):
                shell = True
            else:
                shell = False
                
            result = subprocess.run(
                command, 
                cwd=cwd or self.root_dir, 
                shell=shell,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error ejecutando comando: {e}")
            print(f"Salida: {e.stdout}")
            print(f"Error: {e.stderr}")
            raise
    
    def check_requirements(self):
        """Check if required software is installed"""
        print("🔍 Verificando requerimientos del sistema...")
        
        # Check Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or python_version.minor < 8:
                raise Exception("Python 3.8+ es requerido")
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        except Exception as e:
            print(f"❌ Error de Python: {e}")
            return False
            
        # Check Node.js
        try:
            result = self.run_command(["node", "--version"])
            node_version = result.stdout.strip()
            print(f"✅ Node.js {node_version}")
        except:
            print("❌ Node.js no encontrado. Instale Node.js 18+ desde https://nodejs.org/")
            return False
            
        # Check npm
        try:
            result = self.run_command(["npm", "--version"])
            npm_version = result.stdout.strip()
            print(f"✅ npm {npm_version}")
        except:
            print("❌ npm no encontrado")
            return False
            
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("🐍 Creando entorno virtual de Python...")
        
        if self.venv_dir.exists():
            print("✅ Entorno virtual ya existe")
            return
            
        self.run_command([sys.executable, "-m", "venv", str(self.venv_dir)])
        print("✅ Entorno virtual creado")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📦 Instalando dependencias de Python...")
        
        pip_cmd = self.get_pip_command()
        
        # Upgrade pip
        self.run_command([pip_cmd, "install", "--upgrade", "pip"])
        
        # Install requirements
        requirements_file = self.root_dir / "requirements.txt"
        if requirements_file.exists():
            self.run_command([pip_cmd, "install", "-r", str(requirements_file)])
            print("✅ Dependencias de Python instaladas")
        else:
            print("❌ Archivo requirements.txt no encontrado")
    
    def install_frontend_dependencies(self):
        """Install Node.js dependencies"""
        print("📦 Instalando dependencias del frontend...")
        
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json no encontrado en frontend/")
            return
            
        self.run_command(["npm", "install"], cwd=self.frontend_dir)
        print("✅ Dependencias del frontend instaladas")
    
    def create_environment_files(self):
        """Create environment configuration files"""
        print("⚙️ Creando archivos de configuración...")
        
        # Backend .env
        backend_env = self.backend_dir / ".env"
        if not backend_env.exists():
            env_content = """# ICFES AI Tutor Backend Configuration
DATABASE_URL=sqlite:///./icfes_tutor.db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# OpenAI Configuration (optional)
# OPENAI_API_KEY=your-openai-api-key-here

# Environment
ENVIRONMENT=development
"""
            backend_env.write_text(env_content)
            print("✅ Archivo backend/.env creado")
        
        # Frontend .env.local
        frontend_env = self.frontend_dir / ".env.local"
        if not frontend_env.exists():
            env_content = """# ICFES AI Tutor Frontend Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
"""
            frontend_env.write_text(env_content)
            print("✅ Archivo frontend/.env.local creado")
    
    def initialize_database(self):
        """Initialize the database"""
        print("🗄️ Inicializando base de datos...")
        
        python_cmd = self.get_python_command()
        init_script = self.backend_dir / "app" / "core" / "init_db.py"
        
        if init_script.exists():
            self.run_command([python_cmd, str(init_script)], cwd=self.backend_dir)
            print("✅ Base de datos inicializada")
        else:
            print("⚠️ Script de inicialización de BD no encontrado")
    
    def create_startup_scripts(self):
        """Create startup scripts"""
        print("🚀 Creando scripts de inicio...")
        
        if self.is_windows:
            # Windows batch script
            script_content = f"""@echo off
echo Iniciando ICFES AI Tutor Backend...
cd /d "{self.backend_dir}"
call "{self.venv_dir}\\Scripts\\activate.bat"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
"""
            script_path = self.root_dir / "start_backend.bat"
            script_path.write_text(script_content)
            print("✅ Script start_backend.bat creado")
            
            # Frontend script
            frontend_script = f"""@echo off
echo Iniciando ICFES AI Tutor Frontend...
cd /d "{self.frontend_dir}"
npm run dev
pause
"""
            frontend_script_path = self.root_dir / "start_frontend.bat"
            frontend_script_path.write_text(frontend_script)
            print("✅ Script start_frontend.bat creado")
            
        else:
            # Unix/Linux shell script
            script_content = f"""#!/bin/bash
echo "Iniciando ICFES AI Tutor Backend..."
cd "{self.backend_dir}"
source "{self.venv_dir}/bin/activate"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
"""
            script_path = self.root_dir / "start_backend.sh"
            script_path.write_text(script_content)
            script_path.chmod(0o755)
            print("✅ Script start_backend.sh creado")
            
            # Frontend script
            frontend_script = f"""#!/bin/bash
echo "Iniciando ICFES AI Tutor Frontend..."
cd "{self.frontend_dir}"
npm run dev
"""
            frontend_script_path = self.root_dir / "start_frontend.sh"
            frontend_script_path.write_text(frontend_script)
            frontend_script_path.chmod(0o755)
            print("✅ Script start_frontend.sh creado")
    
    def get_python_command(self):
        """Get the appropriate Python command"""
        if self.is_windows:
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")
    
    def get_pip_command(self):
        """Get the appropriate pip command"""
        if self.is_windows:
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🎯 ICFES AI Tutor - Instalación Automática")
        print("=" * 50)
        
        try:
            if not self.check_requirements():
                print("❌ Requerimientos del sistema no cumplidos")
                return False
                
            self.create_virtual_environment()
            self.install_python_dependencies()
            self.install_frontend_dependencies()
            self.create_environment_files()
            self.initialize_database()
            self.create_startup_scripts()
            
            print("\n🎉 ¡Instalación completada con éxito!")
            print("\nPara iniciar la aplicación:")
            print("1. Backend: Ejecutar start_backend.bat (Windows) o ./start_backend.sh (Linux/Mac)")
            print("2. Frontend: Ejecutar start_frontend.bat (Windows) o ./start_frontend.sh (Linux/Mac)")
            print("3. Abrir http://localhost:3000 en el navegador")
            print("\nCredenciales de prueba:")
            print("  Admin: admin@icfes.com / admin123")
            print("  Usuario: estudiante@ejemplo.com / user123")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la instalación: {e}")
            return False


if __name__ == "__main__":
    setup = ICFESSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1) 