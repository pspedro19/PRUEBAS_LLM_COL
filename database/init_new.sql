-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Instalar extensión pgcrypto para encriptación de contraseñas
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Crear rol admin si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin') THEN
        CREATE ROLE admin WITH LOGIN PASSWORD 'admin123' SUPERUSER;
    END IF;
END$$;

-- Usar la base de datos mathquest_db
\c mathquest_db

-- NO crear tipos enum - usar VARCHAR simples
-- (comentado para evitar conflictos con SQLAlchemy)
-- CREATE TYPE difficulty_level AS ENUM ('principiante', 'intermedio', 'avanzado', 'experto');
-- CREATE TYPE icfes_area AS ENUM ('matematicas', 'lectura_critica', 'ciencias_naturales', 'sociales_ciudadanas', 'ingles');

-- Tabla de clanes
DROP TABLE IF EXISTS clans CASCADE;
CREATE TABLE clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    rank VARCHAR(50) DEFAULT 'Bronce I',
    clan_id INTEGER REFERENCES clans(id),
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

-- Tabla de preguntas ICFES
DROP TABLE IF EXISTS questions CASCADE;
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    explanation TEXT,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_answer VARCHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    area VARCHAR(50) NOT NULL DEFAULT 'matematicas',
    topic VARCHAR(100) NOT NULL,
    subtopic VARCHAR(100),
    difficulty VARCHAR(20) NOT NULL DEFAULT 'intermedio',
    times_answered INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    points_value INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de respuestas de usuarios
DROP TABLE IF EXISTS user_responses CASCADE;
CREATE TABLE user_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    selected_answer VARCHAR(1) NOT NULL CHECK (selected_answer IN ('A', 'B', 'C', 'D')),
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INTEGER,
    session_id VARCHAR(100),
    quiz_mode VARCHAR(50),
    points_earned INTEGER DEFAULT 0,
    difficulty_at_time VARCHAR(20),
    hints_used INTEGER DEFAULT 0,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),
    error_type VARCHAR(100),
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones de usuario
DROP TABLE IF EXISTS user_sessions CASCADE;
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
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
DROP TABLE IF EXISTS study_sessions CASCADE;
CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user_session_id INTEGER REFERENCES user_sessions(id) ON DELETE CASCADE,
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
    accuracy_percentage FLOAT,
    concepts_practiced JSONB,
    concepts_mastered JSONB,
    concepts_struggling JSONB,
    user_satisfaction INTEGER,
    perceived_difficulty INTEGER,
    user_feedback TEXT,
    recommended_next_topics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de respuestas (legacy)
DROP TABLE IF EXISTS responses CASCADE;
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    study_session_id INTEGER REFERENCES study_sessions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN,
    confidence_score FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar clanes de ejemplo
INSERT INTO clans (name, description) VALUES
    ('Guerreros del Saber', 'Clan de los aspirantes más dedicados'),
    ('Magos del Cálculo', 'Expertos en matemáticas y lógica'),
    ('Lectores Legendarios', 'Maestros de la comprensión lectora')
ON CONFLICT (name) DO NOTHING;

-- Insertar usuarios de ejemplo
INSERT INTO users (username, email, password_hash, display_name, avatar_url, level, xp, rank, clan_id, stats, role) VALUES
    ('admin', 'admin@test.com', crypt('admin123', gen_salt('bf')), 'Admin User', '/avatars/admin.png', 25, 287, 'Oro III', 1, '{"LC":23,"MAT":19,"SOC":21,"CIE":20,"ING":18}', 'admin'),
    ('teacher', 'teacher@test.com', crypt('teacher123', gen_salt('bf')), 'Teacher User', '/avatars/teacher.png', 15, 180, 'Plata II', 2, '{"LC":18,"MAT":20,"SOC":17,"CIE":19,"ING":16}', 'teacher'),
    ('student', 'student@test.com', crypt('student123', gen_salt('bf')), 'Student User', '/avatars/student.png', 8, 75, 'Bronce II', 3, '{"LC":8,"MAT":10,"SOC":7,"CIE":9,"ING":6}', 'student')
ON CONFLICT (email) DO NOTHING;

-- Insertar preguntas de matemáticas para cada calabozo
-- ÁLGEBRA BÁSICA - PREGUNTAS REALES TIPO ICFES
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Ecuación lineal básica', 'Si 2x - 3 = 7, entonces el valor de x es:', '2x - 3 = 7 → 2x = 7 + 3 → 2x = 10 → x = 5', '2', '5', '4', '10', 'B', 'matematicas', 'algebra_basica', 'ecuaciones_lineales', 'principiante', 15),
    ('Sistema de ecuaciones simples', 'En un teatro hay 240 asientos distribuidos en 12 filas. Si todas las filas tienen el mismo número de asientos, ¿cuántos asientos hay por fila?', 'Dividimos el total de asientos entre el número de filas: 240 ÷ 12 = 20 asientos por fila', '18', '20', '22', '24', 'B', 'matematicas', 'algebra_basica', 'problemas_aplicacion', 'principiante', 12),
    ('Factorización básica', 'La expresión x² - 9 es equivalente a:', 'x² - 9 es una diferencia de cuadrados: a² - b² = (a-b)(a+b), entonces x² - 3² = (x-3)(x+3)', '(x - 3)(x - 3)', '(x + 3)(x + 3)', '(x - 3)(x + 3)', 'x(x - 9)', 'C', 'matematicas', 'algebra_basica', 'factorizacion', 'principiante', 18),
    ('Proporcionalidad directa', 'Si 5 cuadernos cuestan $15.000, ¿cuánto costarán 8 cuadernos del mismo tipo?', 'Cada cuaderno cuesta $15.000 ÷ 5 = $3.000. Entonces 8 cuadernos cuestan 8 × $3.000 = $24.000', '$18.000', '$20.000', '$24.000', '$25.000', 'C', 'matematicas', 'algebra_basica', 'proporciones', 'principiante', 14),
    ('Desigualdades lineales', '¿Cuál de los siguientes valores de x satisface la desigualdad 2x + 1 > 9?', '2x + 1 > 9 → 2x > 8 → x > 4. Solo x = 5 satisface esta condición', 'x = 3', 'x = 4', 'x = 5', 'x = 2', 'C', 'matematicas', 'algebra_basica', 'desigualdades', 'principiante', 16),
    ('Gráfica de función lineal', 'IMAGEN: Una gráfica muestra una línea recta que pasa por los puntos (0, 2) y (4, 6). ¿Cuál es la ecuación de esta recta?', 'La pendiente es m = (6-2)/(4-0) = 4/4 = 1. La intersección con y es 2. Por tanto: y = x + 2', 'y = x + 2', 'y = 2x + 2', 'y = x + 4', 'y = 4x + 2', 'A', 'matematicas', 'algebra_basica', 'funciones_lineales', 'principiante', 20),
    ('Expresiones algebraicas', 'Si a = 3 y b = -2, el valor de la expresión 2a - 3b + 1 es:', 'Sustituyendo: 2(3) - 3(-2) + 1 = 6 + 6 + 1 = 13', '11', '13', '9', '7', 'B', 'matematicas', 'algebra_basica', 'evaluacion_expresiones', 'principiante', 12),
    ('Ecuación cuadrática simple', 'La ecuación x² = 16 tiene como soluciones:', 'x² = 16 implica x = ±√16 = ±4, por tanto x = 4 o x = -4', 'x = 4 únicamente', 'x = 4 y x = -4', 'x = 8 únicamente', 'x = 2 y x = -2', 'B', 'matematicas', 'algebra_basica', 'ecuaciones_cuadraticas', 'principiante', 18);

-- GEOMETRÍA
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Área del triángulo', 'Un triángulo tiene base 8 cm y altura 6 cm. ¿Cuál es su área?', 'Área = (base × altura) / 2 = (8 × 6) / 2 = 24 cm²', '24 cm²', '48 cm²', '14 cm²', '32 cm²', 'A', 'matematicas', 'geometria', 'triangulos', 'principiante', 10),
    ('Teorema de Pitágoras', 'En un triángulo rectángulo con catetos 3 y 4, ¿cuál es la hipotenusa?', 'h² = 3² + 4² = 9 + 16 = 25, entonces h = 5', '5', '7', '12', '25', 'A', 'matematicas', 'geometria', 'triangulos', 'intermedio', 15),
    ('Circunferencia', '¿Cuál es el área de un círculo con radio 3 cm? (usar π ≈ 3.14)', 'Área = πr² = 3.14 × 3² = 3.14 × 9 = 28.26 cm²', '28.26 cm²', '18.84 cm²', '9 cm²', '6 cm²', 'A', 'matematicas', 'geometria', 'circulos', 'intermedio', 15),
    ('Volumen del cubo', 'Un cubo tiene arista de 4 cm. ¿Cuál es su volumen?', 'Volumen = arista³ = 4³ = 64 cm³', '64 cm³', '16 cm³', '48 cm³', '12 cm³', 'A', 'matematicas', 'geometria', 'volumenes', 'principiante', 10),
    ('Polígonos regulares', '¿Cuántos grados mide cada ángulo interior de un hexágono regular?', 'Ángulo interior = (n-2) × 180° / n = (6-2) × 180° / 6 = 120°', '120°', '108°', '135°', '90°', 'A', 'matematicas', 'geometria', 'poligonos', 'avanzado', 20);

-- TRIGONOMETRÍA
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Seno de 90°', '¿Cuál es el valor de sen(90°)?', 'En el círculo unitario, sen(90°) = 1', '0', '1', '-1', '0.5', 'B', 'matematicas', 'trigonometria', 'funciones_trigonometricas', 'intermedio', 15),
    ('Coseno de 60°', '¿Cuál es el valor de cos(60°)?', 'cos(60°) = 1/2 = 0.5', '0.5', '0.866', '1', '0.707', 'A', 'matematicas', 'trigonometria', 'funciones_trigonometricas', 'intermedio', 15),
    ('Identidad fundamental', 'Si sen(θ) = 0.6, ¿cuál es cos²(θ)?', 'sen²(θ) + cos²(θ) = 1, entonces cos²(θ) = 1 - sen²(θ) = 1 - 0.36 = 0.64', '0.64', '0.8', '0.36', '0.4', 'A', 'matematicas', 'trigonometria', 'identidades', 'avanzado', 20),
    ('Ley del seno', 'En un triángulo, si a/sen(A) = b/sen(B), ¿cómo se llama esta relación?', 'Esta es la Ley del Seno, fundamental en trigonometría', 'Ley del Seno', 'Ley del Coseno', 'Teorema de Pitágoras', 'Identidad trigonométrica', 'A', 'matematicas', 'trigonometria', 'triangulos_oblicuos', 'avanzado', 20),
    ('Periodo de funciones', '¿Cuál es el periodo de la función sen(x)?', 'La función seno tiene periodo 2π', '2π', 'π', 'π/2', '4π', 'A', 'matematicas', 'trigonometria', 'funciones_trigonometricas', 'avanzado', 20);

-- ESTADÍSTICA
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Media aritmética', 'Calcula la media de: 2, 4, 6, 8, 10', 'Media = (2+4+6+8+10)/5 = 30/5 = 6', '6', '5', '7', '8', 'A', 'matematicas', 'estadistica', 'medidas_tendencia', 'principiante', 10),
    ('Mediana', 'En el conjunto {3, 7, 2, 9, 5}, ¿cuál es la mediana?', 'Ordenado: {2, 3, 5, 7, 9}. La mediana es el valor central: 5', '5', '6', '3', '7', 'A', 'matematicas', 'estadistica', 'medidas_tendencia', 'intermedio', 15),
    ('Probabilidad básica', 'Al lanzar un dado, ¿cuál es la probabilidad de obtener un número par?', 'Números pares: 2, 4, 6. Probabilidad = 3/6 = 1/2', '1/2', '1/3', '2/3', '1/6', 'A', 'matematicas', 'estadistica', 'probabilidad', 'intermedio', 15),
    ('Desviación estándar', '¿Qué mide la desviación estándar?', 'La desviación estándar mide la dispersión de los datos respecto a la media', 'Dispersión de datos', 'Valor máximo', 'Tendencia central', 'Correlación', 'A', 'matematicas', 'estadistica', 'medidas_dispersion', 'avanzado', 20),
    ('Correlación', 'Si al aumentar X también aumenta Y, ¿qué tipo de correlación hay?', 'Cuando ambas variables aumentan juntas, hay correlación positiva', 'Correlación positiva', 'Correlación negativa', 'No hay correlación', 'Correlación cuadrática', 'A', 'matematicas', 'estadistica', 'correlacion', 'avanzado', 20);

-- CÁLCULO
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Límite básico', '¿Cuál es lim(x→2) (x² - 4)/(x - 2)?', 'Factorizando: (x² - 4)/(x - 2) = (x+2)(x-2)/(x-2) = x+2. lim(x→2) (x+2) = 4', '4', '2', '0', 'No existe', 'A', 'matematicas', 'calculo', 'limites', 'experto', 30),
    ('Derivada de potencia', '¿Cuál es la derivada de f(x) = x³?', 'Usando la regla de la potencia: d/dx(xⁿ) = nxⁿ⁻¹, entonces d/dx(x³) = 3x²', '3x²', 'x²', '3x', 'x³/3', 'A', 'matematicas', 'calculo', 'derivadas', 'experto', 30),
    ('Integral básica', '¿Cuál es ∫x dx?', 'La integral de x es x²/2 + C', 'x²/2 + C', 'x² + C', 'x/2 + C', '2x + C', 'A', 'matematicas', 'calculo', 'integrales', 'experto', 30),
    ('Regla de la cadena', 'Si f(x) = (2x + 1)³, ¿cuál es f''(x)?', 'Usando regla de la cadena: f''(x) = 3(2x + 1)² × 2 = 6(2x + 1)²', '6(2x + 1)²', '3(2x + 1)²', '(2x + 1)²', '2(2x + 1)²', 'A', 'matematicas', 'calculo', 'derivadas', 'experto', 30),
    ('Serie geométrica', '¿Cuál es la suma de la serie 1 + 1/2 + 1/4 + 1/8 + ...?', 'Es una serie geométrica con a = 1, r = 1/2. Suma = a/(1-r) = 1/(1-1/2) = 2', '2', '1', '∞', '1.5', 'A', 'matematicas', 'calculo', 'series', 'experto', 30);

-- DESAFÍO MIXTO
INSERT INTO questions (title, content, explanation, option_a, option_b, option_c, option_d, correct_answer, area, topic, subtopic, difficulty, points_value) VALUES
    ('Problema mixto 1', 'Un triángulo rectángulo tiene catetos x y x+2. Si su área es 24, ¿cuál es x?', 'Área = (x)(x+2)/2 = 24, entonces x(x+2) = 48, x² + 2x - 48 = 0, (x+8)(x-6) = 0, x = 6', '6', '8', '4', '12', 'A', 'matematicas', 'mixto', 'algebra_geometria', 'avanzado', 25),
    ('Problema mixto 2', 'La probabilidad de lluvia es 0.3. ¿Cuál es la probabilidad de que NO llueva en 2 días consecutivos?', 'P(no lluvia) = 0.7. P(no llueva 2 días) = 0.7 × 0.7 = 0.49', '0.49', '0.09', '0.21', '0.7', 'A', 'matematicas', 'mixto', 'probabilidad_aplicada', 'avanzado', 25),
    ('Problema mixto 3', 'Una función f(x) = 2x + 3. Si f(a) = 11, ¿cuál es a?', 'f(a) = 2a + 3 = 11, entonces 2a = 8, a = 4', '4', '5', '3', '7', 'A', 'matematicas', 'mixto', 'funciones_lineales', 'intermedio', 20),
    ('Problema mixto 4', 'El volumen de un cilindro es πr²h. Si r = 3 y h = 4, ¿cuál es el volumen?', 'V = π(3²)(4) = π(9)(4) = 36π', '36π', '12π', '24π', '18π', 'A', 'matematicas', 'mixto', 'geometria_aplicada', 'intermedio', 20),
    ('Problema mixto 5', 'Una sucesión aritmética tiene primer término 5 y diferencia común 3. ¿Cuál es el 10° término?', 'aₙ = a₁ + (n-1)d = 5 + (10-1)3 = 5 + 27 = 32', '32', '35', '29', '38', 'A', 'matematicas', 'mixto', 'sucesiones', 'avanzado', 25);

-- Crear índices para optimizar consultas
CREATE INDEX idx_questions_area_topic ON questions(area, topic);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_user_responses_user_question ON user_responses(user_id, question_id);
CREATE INDEX idx_user_responses_answered_at ON user_responses(answered_at);

-- Función para actualizar estadísticas de preguntas
CREATE OR REPLACE FUNCTION update_question_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE questions 
    SET times_answered = times_answered + 1,
        times_correct = times_correct + CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
        success_rate = CASE 
            WHEN times_answered + 1 > 0 THEN 
                ((times_correct + CASE WHEN NEW.is_correct THEN 1 ELSE 0 END) * 100.0) / (times_answered + 1)
            ELSE 0 
        END
    WHERE id = NEW.question_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar estadísticas automáticamente
CREATE TRIGGER trigger_update_question_stats
    AFTER INSERT ON user_responses
    FOR EACH ROW
    EXECUTE FUNCTION update_question_stats();

-- Fin del script de la Torre de Babel 