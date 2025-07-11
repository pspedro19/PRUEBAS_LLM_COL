# ICFES Quest - Epic Learning Platform

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PRUEBAS_LLM_COL
   ```

2. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp backend/.env.example backend/backend.env
   
   # Edit the environment file if needed (optional for development)
   # The default values work for Docker development setup
   ```

3. **Start all services with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Test Users

The following test users are available for testing:

1. **Admin User**
   - Email: admin@test.com
   - Password: admin123

2. **Teacher User**
   - Email: teacher@test.com
   - Password: teacher123

3. **Student User**
   - Email: student@test.com
   - Password: student123

## 🎮 Features

- **Epic gamified learning experience** with fantasy RPG elements
- **Interactive quizzes** with real-time feedback and explanations
- **Progress tracking** and achievement system
- **Role-based access control** (Admin, Teacher, Student)
- **Beautiful and responsive UI** with epic effects
- **Secure JWT authentication** system
- **PostgreSQL database** for reliable data storage

## 🧪 Quiz System

### How to Test the Quiz

1. Login at http://localhost:3000/auth/login with any test user
2. Navigate to http://localhost:3000/prueba/matematicas/algebra-basica
3. Click "Comenzar Quiz"
4. Answer 5 questions with automatic progression
5. View final results and feedback

### Quiz Features
- 5 questions per session
- Automatic progression with 3-second feedback display
- Real-time accuracy tracking
- Detailed explanations for each answer
- Final performance summary with personalized feedback

## 🛠️ Development Setup

### Manual Setup (Alternative to Docker)

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example backend.env
   
   # Start backend
   python main_simple.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Setup**
   ```bash
   # The database will be automatically initialized with sample questions
   # when using Docker setup
   ```

## 📁 Project Structure

```
PRUEBAS_LLM_COL/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration and database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── main_simple.py     # Simplified main application
│   └── Dockerfile.simple  # Docker configuration
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/           # Next.js app router
│       ├── components/    # React components
│       └── lib/           # Utilities
├── database/              # Database initialization
│   └── init_new.sql      # Database schema and sample data
└── docker-compose.yml    # Docker services configuration
```

## 🔧 Environment Configuration

The project uses the following environment variables (see `backend/.env.example`):

- **Database**: PostgreSQL connection settings
- **Security**: JWT secrets and token expiration
- **External APIs**: OpenAI integration (optional)
- **CORS**: Frontend-backend communication settings

## 🐳 Docker Services

- **frontend**: Next.js application (port 3000)
- **backend**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)

## 📚 API Documentation

The API documentation is available at http://localhost:8000/docs when the backend is running.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the changes with Docker
5. Submit a pull request

## 📄 License

This project is for educational purposes. 