-- =====================================================
-- BASE DE DATOS COMPLETA - CIUDADELA DEL CONOCIMIENTO ICFES
-- =====================================================
-- Versión: 2.0
-- Motor: MySQL 8.0+
-- Encoding: UTF8MB4
-- =====================================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS ciudadela_icfes 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ciudadela_icfes;

-- =====================================================
-- TABLAS DE USUARIOS Y AUTENTICACIÓN
-- =====================================================

-- Tabla de instituciones educativas
CREATE TABLE schools (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    school_type ENUM('PUBLIC', 'PRIVATE', 'CHARTER') NOT NULL,
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_school_type (school_type),
    INDEX idx_location (city, department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de universidades objetivo
CREATE TABLE universities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    min_icfes_score INT DEFAULT 0,
    logo_url VARCHAR(500),
    website VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla principal de usuarios
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uuid CHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    
    -- Información personal
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    identification_number VARCHAR(20) UNIQUE,
    phone_number VARCHAR(15),
    birth_date DATE,
    
    -- Información académica
    school_id INT,
    grade INT CHECK (grade BETWEEN 9 AND 11),
    target_university_id INT,
    target_career VARCHAR(200),
    
    -- Estado de gamificación
    hero_class ENUM('F','E','D','C','B','A','S','S+') DEFAULT 'F',
    level INT DEFAULT 1,
    experience_points INT DEFAULT 0,
    
    -- Estado de evaluación
    initial_assessment_completed BOOLEAN DEFAULT FALSE,
    initial_assessment_date DATETIME,
    vocational_test_completed BOOLEAN DEFAULT FALSE,
    assigned_role ENUM('TANK','DPS','SUPPORT','SPECIALIST'),
    
    -- Avatar y personalización
    avatar_config JSON,
    avatar_evolution_stage INT DEFAULT 1,
    
    -- Preferencias
    notification_preferences JSON,
    study_schedule JSON,
    preferred_language VARCHAR(5) DEFAULT 'es',
    
    -- Control
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    last_activity DATETIME,
    
    -- Foreign Keys
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL,
    FOREIGN KEY (target_university_id) REFERENCES universities(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_hero_class (hero_class),
    INDEX idx_school (school_id),
    INDEX idx_level (level),
    INDEX idx_active (is_active, last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLAS DE PREGUNTAS ICFES (CLASIFICACIÓN MEJORADA)
-- =====================================================

-- Categorías principales de preguntas
CREATE TABLE question_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tipos de preguntas según formato
CREATE TABLE question_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    requires_figure BOOLEAN DEFAULT FALSE,
    requires_graph BOOLEAN DEFAULT FALSE,
    requires_table BOOLEAN DEFAULT FALSE,
    requires_context BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Conceptos matemáticos
CREATE TABLE concepts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    area VARCHAR(30) NOT NULL,
    parent_concept_id INT,
    difficulty_level INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_concept_id) REFERENCES concepts(id) ON DELETE SET NULL,
    INDEX idx_area (area),
    INDEX idx_parent (parent_concept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Banco de preguntas principal
CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    icfes_id VARCHAR(50) COMMENT 'ID original del ICFES si aplica',
    
    -- Categorización
    category_id INT NOT NULL,
    question_type_id INT NOT NULL,
    
    -- Área y competencias ICFES
    area ENUM('MATEMATICAS','LECTURA_CRITICA','CIENCIAS_NATURALES','SOCIALES_CIUDADANAS','INGLES') NOT NULL,
    
    -- Competencias específicas de matemáticas
    math_competency ENUM('INTERPRETACION','FORMULACION','ARGUMENTACION'),
    math_component ENUM('NUMERICO_VARIACIONAL','GEOMETRICO_METRICO','ALEATORIO'),
    
    -- Contenido de la pregunta
    context TEXT COMMENT 'Contexto o enunciado previo',
    question_text TEXT NOT NULL,
    
    -- Recursos multimedia
    main_image VARCHAR(500),
    figure_data JSON COMMENT 'Datos para renderizar figuras geométricas',
    graph_data JSON COMMENT 'Datos para renderizar gráficas',
    table_data JSON COMMENT 'Datos para renderizar tablas',
    
    -- Opciones y respuesta
    options JSON NOT NULL COMMENT '[{"id": "A", "text": "...", "has_image": false}]',
    correct_answer VARCHAR(10) NOT NULL,
    
    -- Explicación y recursos
    explanation TEXT NOT NULL,
    explanation_video VARCHAR(500),
    step_by_step_solution JSON,
    
    -- Pistas progresivas
    hint_1 TEXT,
    hint_2 TEXT,
    hint_3 TEXT,
    
    -- Metadatos
    difficulty INT NOT NULL CHECK (difficulty BETWEEN 1 AND 10),
    estimated_time INT DEFAULT 120 COMMENT 'Tiempo estimado en segundos',
    cognitive_level ENUM('REMEMBERING','UNDERSTANDING','APPLYING','ANALYZING','EVALUATING','CREATING'),
    
    -- Clasificación adicional basada en el PDF
    requires_calculator BOOLEAN DEFAULT FALSE,
    has_multiple_concepts BOOLEAN DEFAULT FALSE,
    is_word_problem BOOLEAN DEFAULT FALSE,
    has_real_context BOOLEAN DEFAULT FALSE,
    
    -- Estadísticas
    times_answered INT DEFAULT 0,
    times_correct INT DEFAULT 0,
    times_skipped INT DEFAULT 0,
    average_time INT DEFAULT 0,
    last_used DATETIME,
    
    -- Control
    is_active BOOLEAN DEFAULT TRUE,
    is_from_official_exam BOOLEAN DEFAULT FALSE,
    exam_year INT,
    exam_period VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,
    
    -- Foreign Keys
    FOREIGN KEY (category_id) REFERENCES question_categories(id),
    FOREIGN KEY (question_type_id) REFERENCES question_types(id),
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_area_difficulty (area, difficulty),
    INDEX idx_math_classification (math_competency, math_component),
    INDEX idx_cognitive (cognitive_level),
    INDEX idx_stats (times_answered, times_correct),
    INDEX idx_active_area (is_active, area)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relación muchos a muchos: Preguntas - Conceptos
CREATE TABLE question_concepts (
    question_id INT NOT NULL,
    concept_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    
    PRIMARY KEY (question_id, concept_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Prerequisitos entre preguntas
CREATE TABLE question_prerequisites (
    question_id INT NOT NULL,
    prerequisite_id INT NOT NULL,
    
    PRIMARY KEY (question_id, prerequisite_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLAS DE GAMIFICACIÓN
-- =====================================================

-- Distritos de la ciudadela (áreas ICFES)
CREATE TABLE districts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    narrative TEXT,
    icon_url VARCHAR(500),
    background_url VARCHAR(500),
    color_hex VARCHAR(7),
    base_xp_multiplier DECIMAL(3,2) DEFAULT 1.0,
    unlock_requirements JSON,
    district_guardian VARCHAR(100),
    guardian_avatar VARCHAR(500),
    welcome_message TEXT,
    order_index INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order (order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Academias de maestría
CREATE TABLE academies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    district_id INT NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    narrative_intro TEXT,
    
    difficulty_level INT CHECK (difficulty_level BETWEEN 1 AND 10),
    recommended_level INT CHECK (recommended_level BETWEEN 1 AND 50),
    
    phases_config JSON COMMENT 'Configuración de las 3 fases',
    completion_rewards JSON,
    perfect_completion_bonus JSON,
    
    icon_url VARCHAR(500),
    background_url VARCHAR(500),
    boss_avatar VARCHAR(500),
    
    is_active BOOLEAN DEFAULT TRUE,
    order_index INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    INDEX idx_district_order (district_id, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Estado ICFES del usuario
CREATE TABLE icfes_states (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    
    -- Puntajes por área (0-100)
    math_score DECIMAL(5,2) DEFAULT 0 CHECK (math_score BETWEEN 0 AND 100),
    reading_score DECIMAL(5,2) DEFAULT 0 CHECK (reading_score BETWEEN 0 AND 100),
    science_score DECIMAL(5,2) DEFAULT 0 CHECK (science_score BETWEEN 0 AND 100),
    social_score DECIMAL(5,2) DEFAULT 0 CHECK (social_score BETWEEN 0 AND 100),
    english_score DECIMAL(5,2) DEFAULT 0 CHECK (english_score BETWEEN 0 AND 100),
    
    -- Puntaje global (0-500)
    global_score DECIMAL(5,2) DEFAULT 0 CHECK (global_score BETWEEN 0 AND 500),
    
    -- Percentil y predicción
    national_percentile INT DEFAULT 0 CHECK (national_percentile BETWEEN 0 AND 100),
    predicted_score DECIMAL(5,2),
    prediction_confidence DECIMAL(3,2),
    prediction_date DATETIME,
    
    -- Estadísticas
    total_questions_answered INT DEFAULT 0,
    total_correct_answers INT DEFAULT 0,
    total_study_minutes INT DEFAULT 0,
    last_improvement_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_global_score (global_score DESC),
    INDEX idx_percentile (national_percentile DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Progreso por distrito
CREATE TABLE user_district_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    district_id INT NOT NULL,
    
    current_level INT DEFAULT 1 CHECK (current_level BETWEEN 1 AND 10),
    level_progress DECIMAL(5,2) DEFAULT 0,
    total_xp INT DEFAULT 0,
    
    total_questions INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    perfect_streaks INT DEFAULT 0,
    
    academies_completed INT DEFAULT 0,
    academies_total INT DEFAULT 0,
    
    last_activity DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_user_district (user_id, district_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY