-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Crear rol admin si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin') THEN
        CREATE ROLE admin WITH LOGIN PASSWORD 'admin123' SUPERUSER;
    END IF;
END$$;

-- Crear base de datos si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mathquest_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE mathquest_db OWNER admin');
    END IF;
END$$;

-- Usar la base de datos
\c mathquest_db

-- Tabla de clanes
CREATE TABLE IF NOT EXISTS clans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    rank VARCHAR(50) DEFAULT 'Bronce I',
    clan_id UUID REFERENCES clans(id),
    stats JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auth_provider VARCHAR(20) DEFAULT 'email',
    google_id VARCHAR(255) UNIQUE,
    microsoft_id VARCHAR(255) UNIQUE,
    role VARCHAR(20) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    verification_token VARCHAR(255),
    reset_password_token VARCHAR(255),
    reset_password_expires TIMESTAMP
);

-- Tabla de preguntas
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discipline VARCHAR(50) NOT NULL,
    difficulty INTEGER NOT NULL,
    topic VARCHAR(100),
    question_text TEXT NOT NULL UNIQUE,
    options JSONB NOT NULL,
    correct_option VARCHAR(10) NOT NULL,
    reward_xp INTEGER DEFAULT 10,
    reward_item VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de respuestas
CREATE TABLE IF NOT EXISTS responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    study_session_id UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN,
    confidence_score FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones de usuario
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(20),
    browser VARCHAR(50),
    operating_system VARCHAR(50),
    country VARCHAR(2),
    city VARCHAR(100),
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_suspicious BOOLEAN DEFAULT FALSE,
    security_flags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Tabla de sesiones de estudio
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_session_id UUID REFERENCES user_sessions(id) ON DELETE CASCADE,
    session_type VARCHAR(20) DEFAULT 'practice',
    subject_area VARCHAR(30),
    target_competencies JSONB,
    planned_duration_minutes INTEGER,
    planned_questions INTEGER,
    difficulty_target VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    current_question_index INTEGER DEFAULT 0,
    total_questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_active_time_ms INTEGER DEFAULT 0,
    starting_theta JSONB,
    ending_theta JSONB,
    theta_improvement JSONB,
    average_response_time_ms INTEGER,
    fastest_response_time_ms INTEGER,
    slowest_response_time_ms INTEGER,
    accuracy_percentage FLOAT,
    concepts_practiced JSONB,
    concepts_mastered JSONB,
    concepts_struggling JSONB,
    engagement_score FLOAT,
    focus_score FLOAT,
    persistence_score FLOAT,
    user_satisfaction INTEGER,
    perceived_difficulty INTEGER,
    user_feedback TEXT,
    recommended_next_topics JSONB,
    pause_count INTEGER DEFAULT 0,
    total_pause_time_ms INTEGER DEFAULT 0,
    interruption_reasons JSONB,
    ai_recommendations JSONB,
    learning_path_adjustments JSONB,
    performance_insights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar clanes de ejemplo
INSERT INTO clans (id, name, description) VALUES
    (uuid_generate_v4(), 'Guerreros del Saber', 'Clan de los aspirantes más dedicados'),
    (uuid_generate_v4(), 'Magos del Cálculo', 'Expertos en matemáticas y lógica'),
    (uuid_generate_v4(), 'Lectores Legendarios', 'Maestros de la comprensión lectora')
ON CONFLICT (name) DO NOTHING;

-- Insertar usuarios de ejemplo
INSERT INTO users (id, username, email, password_hash, display_name, avatar_url, level, xp, rank, clan_id, stats) VALUES
    (uuid_generate_v4(), 'admin', 'admin@icfes.com', crypt('admin123', gen_salt('bf')), 'Administrador', '/avatars/admin.png', 25, 287, 'Oro III', (SELECT id FROM clans WHERE name='Guerreros del Saber'), '{"LC":23,"MAT":19,"SOC":21,"CIE":20,"ING":18}'),
    (uuid_generate_v4(), 'test', 'test@example.com', crypt('test123', gen_salt('bf')), 'Test User', '/avatars/test.png', 10, 100, 'Plata I', (SELECT id FROM clans WHERE name='Magos del Cálculo'), '{"LC":10,"MAT":12,"SOC":9,"CIE":11,"ING":8}'),
    (uuid_generate_v4(), 'epico', 'epico@anime.com', crypt('epicpass', gen_salt('bf')), 'Aspirante Supremo', '/avatars/epico.png', 30, 400, 'Diamante', (SELECT id FROM clans WHERE name='Lectores Legendarios'), '{"LC":30,"MAT":28,"SOC":27,"CIE":29,"ING":25}')
ON CONFLICT (email) DO NOTHING;

-- Insertar preguntas de ejemplo (Matemáticas)
INSERT INTO questions (id, discipline, difficulty, topic, question_text, options, correct_option, reward_xp, reward_item) VALUES
    (uuid_generate_v4(), 'MAT', 2, 'Ecuaciones', '¿Cuál es el valor de x en 2x + 5 = 15?', '[{"id":"A","text":"x = 5"},{"id":"B","text":"x = 10"},{"id":"C","text":"x = 7.5"},{"id":"D","text":"x = 20"}]', 'A', 15, 'Poción de Concentración'),
    (uuid_generate_v4(), 'MAT', 3, 'Trigonometría', '¿Cuál es el seno de 90°?', '[{"id":"A","text":"0"},{"id":"B","text":"1"},{"id":"C","text":"-1"},{"id":"D","text":"0.5"}]', 'B', 20, 'Item raro'),
    (uuid_generate_v4(), 'LC', 2, 'Comprensión', '¿Cuál es la idea principal del texto anterior?', '[{"id":"A","text":"El autor critica"},{"id":"B","text":"El autor explica"},{"id":"C","text":"El autor narra"},{"id":"D","text":"El autor describe"}]', 'B', 10, NULL)
ON CONFLICT (question_text) DO NOTHING;

-- Insertar respuestas de ejemplo
INSERT INTO responses (id, user_id, question_id, answer_text, is_correct, confidence_score, feedback) VALUES
    (uuid_generate_v4(), (SELECT id FROM users WHERE username='admin'), (SELECT id FROM questions WHERE topic='Ecuaciones'), 'x = 5', TRUE, 0.95, '¡Correcto!'),
    (uuid_generate_v4(), (SELECT id FROM users WHERE username='test'), (SELECT id FROM questions WHERE topic='Trigonometría'), '1', TRUE, 0.90, '¡Bien hecho!')
ON CONFLICT DO NOTHING;

-- Fin del script épico 